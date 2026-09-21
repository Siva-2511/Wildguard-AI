import io
import pandas as pd
from dateutil import parser
from datetime import datetime
from config import MAX_FILE_SIZE_MB

REQUIRED_COLUMNS = ['date', 'time', 'zone', 'species', 'incident_type', 'damage_description', 'resolved']

def parse_date_safe(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    try:
        # Try parsing date using dateutil
        dt = parser.parse(str(val), dayfirst=False)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        try:
            dt = parser.parse(str(val), dayfirst=True)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return None

def parse_time_safe(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    val_str = str(val).strip()
    for fmt in ('%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p'):
        try:
            t = datetime.strptime(val_str, fmt).time()
            return t.strftime('%H:%M')
        except ValueError:
            continue
    try:
        # Fallback with dateutil parser
        dt = parser.parse(val_str)
        return dt.time().strftime('%H:%M')
    except Exception:
        return None

def normalize_resolved(val):
    if pd.isna(val) or str(val).strip() == '':
        return 'Unknown'
    s = str(val).strip().lower()
    if s in ['yes', 'true', '1', 'y']:
        return 'Yes'
    elif s in ['no', 'false', '0', 'n']:
        return 'No'
    else:
        return 'Unknown'

def validate_csv(file_storage):
    warnings = []
    errors = []
    
    # 1. File existence & type check
    if not file_storage or file_storage.filename == '':
        errors.append("No file selected. Please upload a CSV file.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    if not file_storage.filename.lower().endswith('.csv'):
        errors.append("Unsupported file type. Please upload a CSV file (.csv).")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # 2. Read into memory and check size
    try:
        raw_bytes = file_storage.read()
    except Exception:
        errors.append("The file could not be read. Please try again.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    if len(raw_bytes) == 0:
        errors.append("The uploaded file is empty. Please check the file and re-upload.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(raw_bytes) > max_bytes:
        errors.append(f"File exceeds the {MAX_FILE_SIZE_MB} MB size limit. Please upload a smaller file.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # 3. Parse CSV
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes), encoding='utf-8-sig', dtype=str)
    except Exception:
        errors.append("The file could not be read as a CSV. It may be corrupted or in an unsupported format.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    if df.empty:
        errors.append("The uploaded file is empty. Please check the file and re-upload.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # Normalize column names (strip whitespace and lower case for check)
    col_map = {col: col.strip().lower() for col in df.columns}
    df.rename(columns=col_map, inplace=True)

    # Check required columns — report ALL missing at once
    missing_cols = [req for req in REQUIRED_COLUMNS if req not in df.columns]
    if missing_cols:
        quoted = ", ".join(f"'{c}'" for c in missing_cols)
        errors.append(f"Required column(s) not found: {quoted}. Check column headers and re-upload.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    initial_count = len(df)

    # Strip whitespace from all string columns
    for col in REQUIRED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    # Deduplication
    df_dedup = df.drop_duplicates(subset=REQUIRED_COLUMNS)
    duplicates_removed = initial_count - len(df_dedup)
    if duplicates_removed > 0:
        warnings.append(f"{duplicates_removed} exact duplicate rows removed.")
    df = df_dedup.copy()

    # Required field validation (date, zone, species, incident_type must be non-empty)
    valid_rows = []
    excluded_required = 0
    invalid_dates = 0
    missing_times = 0
    unknown_resolved = 0
    empty_descriptions = 0

    for idx, row in df.iterrows():
        r_date = row['date']
        r_zone = row['zone']
        r_species = row['species']
        r_type = row['incident_type']
        r_time = row['time']
        r_resolved = row['resolved']
        r_desc = row['damage_description']

        # Check required fields non-empty ('nan' check included)
        if not r_date or r_date.lower() == 'nan' or \
           not r_zone or r_zone.lower() == 'nan' or \
           not r_species or r_species.lower() == 'nan' or \
           not r_type or r_type.lower() == 'nan':
            excluded_required += 1
            continue

        # Date parse
        parsed_date = parse_date_safe(r_date)
        if not parsed_date:
            invalid_dates += 1
            continue

        # Time parse
        parsed_time = parse_time_safe(r_time)
        if not parsed_time:
            missing_times += 1

        # Resolved normalisation
        norm_res = normalize_resolved(r_resolved)
        if norm_res == 'Unknown' and r_resolved and r_resolved.lower() != 'nan':
            unknown_resolved += 1

        if not r_desc or r_desc.lower() == 'nan':
            empty_descriptions += 1

        valid_rows.append({
            'date': str(parsed_date),
            'time': str(parsed_time) if parsed_time else '',
            'zone': str(r_zone).title(),
            'species': str(r_species).title(),
            'incident_type': str(r_type).title(),
            'damage_description': str(r_desc) if (r_desc and str(r_desc).lower() != 'nan') else '',
            'resolved': str(norm_res)
        })

    if excluded_required > 0:
        warnings.append(f"{excluded_required} rows excluded due to missing required values (date, zone, or species).")

    if invalid_dates > 0:
        warnings.append(f"{invalid_dates} rows excluded: unrecognisable date format.")

    if missing_times > 0:
        warnings.append(f"{missing_times} rows missing/invalid time values — excluded from time-of-day analysis only.")

    if unknown_resolved > 0:
        warnings.append(f"{unknown_resolved} resolved values unrecognised — treated as Unknown.")

    if empty_descriptions == len(valid_rows) and len(valid_rows) > 0:
        warnings.append("damage_description is empty for all records.")

    clean_df = pd.DataFrame(valid_rows)

    if len(clean_df) < 5:
        errors.append(f"Only {len(clean_df)} valid records found after validation. A minimum of 5 records is required.")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    if len(clean_df) < 20:
        warnings.append(f"Dataset contains only {len(clean_df)} records. Patterns should be interpreted cautiously.")

    # Reporting period
    min_date = clean_df['date'].min()
    max_date = clean_df['date'].max()

    summary = {
        'total_records': len(clean_df),
        'initial_records': initial_count,
        'excluded_records': initial_count - len(clean_df),
        'period_start': min_date,
        'period_end': max_date
    }

    return {
        'valid': True,
        'errors': [],
        'warnings': warnings,
        'summary': summary,
        'data': clean_df.to_dict(orient='records')
    }
