REPORT_PROMPT = """
You are assisting a wildlife conservation programme officer in preparing a monthly 
Human-Wildlife Conflict (HWC) incident report. Your role is to convert structured 
analytical results into a professional, clearly written report draft.

STRICT INSTRUCTIONS — READ CAREFULLY:

1. Use ONLY the data provided below. Do not add facts, species, locations, statistics, 
   causes, or claims not present in the provided data.
2. Never invent incidents, percentages, species names, zone names, or dates.
3. Never state or imply causation. Only describe observed distributions from logged records.
4. Use qualified, cautious language throughout:
   - Use: "observed pattern", "recorded distribution", "largest share of logged incidents",
     "based on available records", "most frequently recorded time period"
   - Do not use: "hotspot", "significant increase", "statistically significant", 
     "proves", "indicates a cause", "confirms"
5. If the dataset is small (flagged below), reflect this caution in the text.
6. Keep mitigation considerations as practical suggestions only — not directives.
   Use language such as "officers may wish to consider", "it may be worthwhile to review",
   "the pattern observed in these records could warrant".
7. Do not make enforcement recommendations.
8. Label the output clearly as a draft requiring human review.
9. Produce exactly the sections listed below, in order. Do NOT add any preamble, title, or header before SECTION 1.
10. Keep each section concise and professional. Total report length: 400–600 words.

--- ANALYSIS DATA ---
Reporting period: {period}
Total valid records analysed: {total_records}
Records excluded during validation: {excluded_records}
Records with valid time (used for time-of-day analysis): {timed_records}
Small dataset flag: {small_sample}

Species distribution:
{species_table}

Zone distribution:
{zone_table}

Incident type distribution:
{type_table}

Time-of-day distribution (based on {timed_records} timed records):
{bracket_table}

Resolution status:
{resolution_table}

Automatically generated pattern observations (from statistical analysis):
{pattern_statements}
--- END OF ANALYSIS DATA ---

Produce the following report sections in order:

SECTION 1 — INCIDENT SUMMARY
A brief factual overview of the reporting period, total incidents, and overall distribution.

SECTION 2 — SPECIES PATTERN
Describe the species distribution observed in the records. Use qualified language.

SECTION 3 — ZONE / CONCENTRATION PATTERN
Describe the zone distribution observed. Note the zone with the highest recorded share.
Do not call any zone a "hotspot" — use "highest recorded concentration of logged incidents."

SECTION 4 — TIME-OF-DAY PATTERN
Describe the time-of-day distribution. If the small_sample flag is true or timed_records 
is fewer than 10, note that time-of-day patterns should be interpreted cautiously.

SECTION 5 — INCIDENT TYPE PATTERN
Describe the incident type distribution.

SECTION 6 — RESOLUTION STATUS
Report the resolved/unresolved distribution. Note which zone has the highest concentration 
of unresolved incidents if that data was provided.

SECTION 7 — KEY OBSERVATIONS
2–3 bullet points summarising the most notable patterns from the data. 
Every statement must be traceable to the data above. No invented observations.

SECTION 8 — SUGGESTED MITIGATION CONSIDERATIONS
2–3 practical, non-directive suggestions that follow logically from the observed patterns.
Use cautious, suggestion-oriented language. These are considerations for the reviewing 
officer, not instructions.
"""

def format_table_str(items_list):
    if not items_list:
        return "None recorded"
    lines = []
    for item in items_list:
        lines.append(f"- {item['name']}: {item['count']} records ({item['pct']}%)")
    return "\n".join(lines)

def build_prompt(stats, summary_info=None):
    if summary_info is None:
        summary_info = {}

    period = stats.get('period_formatted', 'Unknown')
    total_records = stats.get('total_records', 0)
    excluded_records = summary_info.get('excluded_records', 0)
    timed_records = stats.get('timed_records', 0)
    small_sample = "Yes" if stats.get('small_sample', False) else "No"

    species_table = format_table_str(stats.get('species', []))
    zone_table = format_table_str(stats.get('zones', []))
    type_table = format_table_str(stats.get('types', []))
    bracket_table = format_table_str(stats.get('brackets', []))
    
    res = stats.get('resolved', {})
    res_lines = [
        f"- Resolved (Yes): {res.get('Yes', 0)}",
        f"- Unresolved (No): {res.get('No', 0)}",
        f"- Unknown: {res.get('Unknown', 0)}"
    ]
    if stats.get('top_unresolved_zone'):
        res_lines.append(f"- Highest concentration of unresolved incidents: {stats['top_unresolved_zone']} ({stats['top_unresolved_count']} unresolved records)")
    resolution_table = "\n".join(res_lines)

    pattern_stmts = "\n".join([f"- {s}" for s in stats.get('pattern_statements', [])])

    return REPORT_PROMPT.format(
        period=period,
        total_records=total_records,
        excluded_records=excluded_records,
        timed_records=timed_records,
        small_sample=small_sample,
        species_table=species_table,
        zone_table=zone_table,
        type_table=type_table,
        bracket_table=bracket_table,
        resolution_table=resolution_table,
        pattern_statements=pattern_stmts
    )
