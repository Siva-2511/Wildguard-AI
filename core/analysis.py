import pandas as pd
from datetime import datetime


def compute_confidence(stats, summary=None):
    """
    Compute a data confidence score (0–100) based on record quality indicators.
    Returns a dict with overall score, grade, and individual factor breakdowns.
    Pure Python — no AI involved.
    """
    if summary is None:
        summary = {}

    total = stats.get('total_records', 0)
    timed = stats.get('timed_records', 0)
    excluded = summary.get('excluded_records', 0)
    initial = summary.get('initial_records', total + excluded) or 1
    small = stats.get('small_sample', False)

    factors = []
    score = 0

    # Factor 1: Record volume (30 pts)
    if total >= 50:
        pts, label, status = 30, f'{total} records (Good, 50+)', 'good'
    elif total >= 20:
        pts, label, status = 20, f'{total} records (Moderate, 20-49)', 'moderate'
    else:
        pts, label, status = 8, f'{total} records (Low, under 20)', 'low'
    score += pts
    factors.append({'label': 'Record volume', 'detail': label, 'status': status})

    # Factor 2: Time coverage (25 pts)
    time_pct = round(timed / total * 100) if total > 0 else 0
    if time_pct >= 90:
        pts, label, status = 25, f'{time_pct}% records have valid time (Good)', 'good'
    elif time_pct >= 60:
        pts, label, status = 15, f'{time_pct}% records have valid time (Moderate)', 'moderate'
    else:
        pts, label, status = 5, f'{time_pct}% records have valid time (Low)', 'low'
    score += pts
    factors.append({'label': 'Time coverage', 'detail': label, 'status': status})

    # Factor 3: Data completeness — excluded rows (20 pts)
    exclusion_pct = round(excluded / initial * 100) if initial > 0 else 0
    if exclusion_pct == 0:
        pts, label, status = 20, 'No records excluded during validation (Excellent)', 'good'
    elif exclusion_pct <= 5:
        pts, label, status = 15, f'{exclusion_pct}% records excluded (Good)', 'good'
    elif exclusion_pct <= 15:
        pts, label, status = 8, f'{exclusion_pct}% records excluded (Moderate)', 'moderate'
    else:
        pts, label, status = 2, f'{exclusion_pct}% records excluded (High data loss)', 'low'
    score += pts
    factors.append({'label': 'Data completeness', 'detail': label, 'status': status})

    # Factor 4: Resolution tracking (15 pts)
    unknown_res = stats.get('resolved', {}).get('Unknown', 0)
    unknown_pct = round(unknown_res / total * 100) if total > 0 else 0
    if unknown_pct == 0:
        pts, label, status = 15, 'All resolution statuses recorded (Excellent)', 'good'
    elif unknown_pct <= 10:
        pts, label, status = 10, f'{unknown_pct}% resolution status unknown (Good)', 'good'
    else:
        pts, label, status = 4, f'{unknown_pct}% resolution status unknown (Incomplete)', 'moderate'
    score += pts
    factors.append({'label': 'Resolution tracking', 'detail': label, 'status': status})

    # Factor 5: Trend context (10 pts)
    if small:
        pts, label, status = 0, 'Single small dataset — no trend comparison (Caution)', 'low'
    else:
        pts, label, status = 10, 'Sufficient records for pattern analysis', 'good'
    score += pts
    factors.append({'label': 'Sample sufficiency', 'detail': label, 'status': status})

    # Grade
    if score >= 85:
        grade, grade_label = 'high', 'High'
    elif score >= 60:
        grade, grade_label = 'medium', 'Medium'
    else:
        grade, grade_label = 'low', 'Low'

    return {
        'score': score,
        'grade': grade,
        'grade_label': grade_label,
        'factors': factors,
    }

def assign_bracket(time_str):
    if not time_str or time_str == '':
        return None
    try:
        t = datetime.strptime(time_str, '%H:%M').time()
        h = t.hour
        if 6 <= h <= 11:
            return 'Morning (06:00–11:59)'
        elif 12 <= h <= 16:
            return 'Afternoon (12:00–16:59)'
        elif 17 <= h <= 20:
            return 'Evening (17:00–20:59)'
        else:
            return 'Night (21:00–05:59)'
    except Exception:
        return None

def build_pattern_statements(stats, total_records):
    stmts = []

    if total_records < 20:
        stmts.append(
            f"Note: This analysis is based on {total_records} records. "
            "Observed patterns should be interpreted with caution."
        )

    # Zone statement
    if stats['zones']:
        top_z = stats['zones'][0]
        stmts.append(
            f"{top_z['name']} recorded the highest share of logged incidents "
            f"({top_z['count']} of {total_records}, {top_z['pct']}%)."
        )

    # Species statement
    if stats['species']:
        top_s = stats['species'][0]
        stmts.append(
            f"{top_s['name']} incidents represented the largest recorded species category "
            f"({top_s['count']} of {total_records}, {top_s['pct']}%)."
        )

    # Time statement
    if stats['timed_records'] >= 5 and len(stats['brackets']) > 0:
        top_b = stats['brackets'][0]
        stmts.append(
            f"{top_b['name']} was the most frequently recorded time period "
            f"({top_b['count']} of {stats['timed_records']} timed records, {top_b['pct']}%)."
        )

    # Resolution statement
    unresolved_count = stats['resolved'].get('No', 0)
    unresolved_pct = round(unresolved_count / total_records * 100, 1) if total_records > 0 else 0
    stmts.append(
        f"{unresolved_count} incidents ({unresolved_pct}%) remain recorded as unresolved."
    )

    return stmts

def run_analysis(records):
    df = pd.DataFrame(records)
    total_records = len(df)

    # Reporting period string
    min_d = pd.to_datetime(df['date']).min()
    max_d = pd.to_datetime(df['date']).max()
    period_str = f"{min_d.strftime('%d %B %Y')} – {max_d.strftime('%d %B %Y')}"
    month_year_str = min_d.strftime('%B %Y')

    # Species breakdown
    sp_counts = df['species'].value_counts()
    species_list = []
    for name, count in sp_counts.items():
        species_list.append({
            'name': name,
            'count': int(count),
            'pct': round(float(count / total_records * 100), 1)
        })

    # Zone breakdown
    zone_counts = df['zone'].value_counts()
    zone_list = []
    for name, count in zone_counts.items():
        zone_list.append({
            'name': name,
            'count': int(count),
            'pct': round(float(count / total_records * 100), 1)
        })

    # Incident Type breakdown
    type_counts = df['incident_type'].value_counts()
    type_list = []
    for name, count in type_counts.items():
        type_list.append({
            'name': name,
            'count': int(count),
            'pct': round(float(count / total_records * 100), 1)
        })

    # Time bracket breakdown
    df['bracket'] = df['time'].apply(assign_bracket)
    timed_df = df.dropna(subset=['bracket'])
    timed_records_count = len(timed_df)

    bracket_list = []
    if timed_records_count > 0:
        b_counts = timed_df['bracket'].value_counts()
        for name, count in b_counts.items():
            bracket_list.append({
                'name': name,
                'count': int(count),
                'pct': round(float(count / timed_records_count * 100), 1)
            })

    # Resolution breakdown
    res_counts = df['resolved'].value_counts()
    res_dict = {
        'Yes': int(res_counts.get('Yes', 0)),
        'No': int(res_counts.get('No', 0)),
        'Unknown': int(res_counts.get('Unknown', 0))
    }
    res_list = [
        {'name': 'Resolved (Yes)', 'count': res_dict['Yes'], 'pct': round(res_dict['Yes']/total_records*100, 1)},
        {'name': 'Unresolved (No)', 'count': res_dict['No'], 'pct': round(res_dict['No']/total_records*100, 1)},
        {'name': 'Unknown', 'count': res_dict['Unknown'], 'pct': round(res_dict['Unknown']/total_records*100, 1)}
    ]

    # Unresolved by Zone
    unresolved_df = df[df['resolved'] == 'No']
    top_unresolved_zone = None
    top_unresolved_count = 0
    if not unresolved_df.empty:
        u_zone_counts = unresolved_df['zone'].value_counts()
        top_unresolved_zone = u_zone_counts.index[0]
        top_unresolved_count = int(u_zone_counts.iloc[0])

    stats = {
        'period_formatted': period_str,
        'month_year': month_year_str,
        'total_records': total_records,
        'timed_records': timed_records_count,
        'species': species_list,
        'zones': zone_list,
        'types': type_list,
        'brackets': bracket_list,
        'resolved': res_dict,
        'resolved_list': res_list,
        'top_unresolved_zone': top_unresolved_zone,
        'top_unresolved_count': top_unresolved_count,
        'small_sample': total_records < 20
    }

    stats['pattern_statements'] = build_pattern_statements(stats, total_records)
    return stats
