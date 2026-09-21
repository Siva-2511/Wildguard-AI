import os
import json
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

DEMO_REPORT_TEXT = """SECTION 1 — INCIDENT SUMMARY
During the reporting period of {period}, a total of {total_records} incident records were logged across the conservancy zones. Crop raids represented the most frequently recorded incident type. Elephant was the most recorded species. A total of {unresolved_count} incidents ({unresolved_pct}%) remain recorded as unresolved at the time of this report.

SECTION 2 — SPECIES PATTERN
Based on available records, {top_species} incidents represented the largest recorded species category, accounting for {top_species_count} of {total_records} records ({top_species_pct}%). Subsequent recorded species included {other_species}. These figures reflect the distribution within the logged dataset for this period.

SECTION 3 — ZONE / CONCENTRATION PATTERN
{top_zone} recorded the highest share of logged incidents during this period, with {top_zone_count} of {total_records} records ({top_zone_pct}%). Incident records were also logged in {other_zones}. This distribution represents the observed concentration pattern within the available dataset.

SECTION 4 — TIME-OF-DAY PATTERN
Among the {timed_records} incident records with valid time values, {top_bracket} was the most frequently recorded time period, accounting for {top_bracket_count} records ({top_bracket_pct}% of timed incidents). Other recorded time periods included {other_brackets}.

SECTION 5 — INCIDENT TYPE PATTERN
{top_type} was the most frequently recorded incident type, accounting for {top_type_count} of {total_records} records ({top_type_pct}%). Other recorded incident types included {other_types}.

SECTION 6 — RESOLUTION STATUS
{resolved_count} of the {total_records} recorded incidents ({resolved_pct}%) are recorded as resolved. {unresolved_count} incidents ({unresolved_pct}%) remain recorded as unresolved. {top_unresolved_clause}

SECTION 7 — KEY OBSERVATIONS
- {top_zone} recorded the highest share of logged incidents for this period ({top_zone_pct}%), with {top_species} incidents as the dominant recorded species category.
- {top_bracket} was the most frequently recorded time period ({top_bracket_pct}% of timed incidents) — an observed pattern relevant to patrol planning.
- {unresolved_pct}% of incidents remain recorded as unresolved, with the highest concentration of unresolved records in {top_unresolved_zone_name}.

SECTION 8 — SUGGESTED MITIGATION CONSIDERATIONS
- Given the observed concentration of incidents during {top_bracket} in {top_zone}, officers may wish to review current patrol scheduling for that zone and time period.
- The high proportion of {top_species} {top_type} incidents recorded during this period may warrant a review of existing deterrent measures and boundary buffer conditions.
- The {unresolved_count} unresolved incidents, concentrated in {top_unresolved_zone_name}, may benefit from a follow-up review to determine whether status updates are pending or further response is needed.
"""

def generate_fallback_report(stats):
    period = stats.get('period_formatted', 'the reporting period')
    total_records = stats.get('total_records', 0)
    
    unresolved_count = stats['resolved'].get('No', 0)
    unresolved_pct = round(unresolved_count / total_records * 100, 1) if total_records > 0 else 0
    resolved_count = stats['resolved'].get('Yes', 0)
    resolved_pct = round(resolved_count / total_records * 100, 1) if total_records > 0 else 0

    top_species = stats['species'][0]['name'] if stats['species'] else 'Unspecified'
    top_species_count = stats['species'][0]['count'] if stats['species'] else 0
    top_species_pct = stats['species'][0]['pct'] if stats['species'] else 0
    other_species_items = [f"{s['name']} ({s['count']})" for s in stats['species'][1:]]
    other_species = ", ".join(other_species_items) if other_species_items else "no other species"

    top_zone = stats['zones'][0]['name'] if stats['zones'] else 'Unspecified'
    top_zone_count = stats['zones'][0]['count'] if stats['zones'] else 0
    top_zone_pct = stats['zones'][0]['pct'] if stats['zones'] else 0
    other_zones_items = [f"{z['name']} ({z['count']})" for z in stats['zones'][1:]]
    other_zones = ", ".join(other_zones_items) if other_zones_items else "no other zones"

    top_bracket = stats['brackets'][0]['name'] if stats['brackets'] else 'Unspecified'
    top_bracket_count = stats['brackets'][0]['count'] if stats['brackets'] else 0
    top_bracket_pct = stats['brackets'][0]['pct'] if stats['brackets'] else 0
    other_brackets_items = [f"{b['name']} ({b['count']})" for b in stats['brackets'][1:]]
    other_brackets = ", ".join(other_brackets_items) if other_brackets_items else "no other time brackets"

    top_type = stats['types'][0]['name'] if stats['types'] else 'Unspecified'
    top_type_count = stats['types'][0]['count'] if stats['types'] else 0
    top_type_pct = stats['types'][0]['pct'] if stats['types'] else 0
    other_types_items = [f"{t['name']} ({t['count']})" for t in stats['types'][1:]]
    other_types = ", ".join(other_types_items) if other_types_items else "no other types"

    top_unresolved_zone_name = stats.get('top_unresolved_zone') or top_zone
    top_unresolved_clause = f"{top_unresolved_zone_name} had the highest recorded concentration of unresolved incidents." if stats.get('top_unresolved_zone') else ""

    text = DEMO_REPORT_TEXT.format(
        period=period,
        total_records=total_records,
        unresolved_count=unresolved_count,
        unresolved_pct=unresolved_pct,
        resolved_count=resolved_count,
        resolved_pct=resolved_pct,
        top_species=top_species,
        top_species_count=top_species_count,
        top_species_pct=top_species_pct,
        other_species=other_species,
        top_zone=top_zone,
        top_zone_count=top_zone_count,
        top_zone_pct=top_zone_pct,
        other_zones=other_zones,
        timed_records=stats.get('timed_records', 0),
        top_bracket=top_bracket,
        top_bracket_count=top_bracket_count,
        top_bracket_pct=top_bracket_pct,
        other_brackets=other_brackets,
        top_type=top_type,
        top_type_count=top_type_count,
        top_type_pct=top_type_pct,
        other_types=other_types,
        top_unresolved_clause=top_unresolved_clause,
        top_unresolved_zone_name=top_unresolved_zone_name
    )

    return {
        'text': text,
        'is_demo': True,
        'model_used': 'Static Fallback Demo Engine'
    }

# Site URL exposed to OpenRouter — set SITE_URL in .env for production
import os as _os
_SITE_URL = _os.environ.get("SITE_URL", "http://localhost:5000")

def generate_report(prompt, stats):
    api_key = OPENROUTER_API_KEY.strip() if OPENROUTER_API_KEY else ""
    if not api_key:
        print("[llm_client] No OpenRouter API key provided. Using fallback demo report.")
        return generate_fallback_report(stats)

    model = OPENROUTER_MODEL.strip() if OPENROUTER_MODEL else "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": _SITE_URL,
        "X-Title": "WildGuard Report AI"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 3500
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90
        )
        if response.status_code == 200:
            data = response.json()
            # OpenRouter may return HTTP 200 with an upstream error payload
            if data.get("error"):
                print(f"[llm_client] OpenRouter upstream error: {data['error'].get('message','')[:200]}")
                return generate_fallback_report(stats)
            choices = data.get("choices", [])
            if choices and choices[0].get("message", {}).get("content"):
                report_text = choices[0]["message"]["content"]
                return {
                    'text': report_text,
                    'is_demo': False,
                    'model_used': model
                }
            else:
                print("[llm_client] Unexpected response structure from OpenRouter:", data)
                return generate_fallback_report(stats)
        elif response.status_code == 401:
            print("[llm_client] OpenRouter 401 — invalid API key.")
            return generate_fallback_report(stats)
        elif response.status_code == 429:
            print("[llm_client] OpenRouter 429 — rate limit hit.")
            return generate_fallback_report(stats)
        else:
            print(f"[llm_client] OpenRouter API error {response.status_code}: {response.text[:300]}")
            return generate_fallback_report(stats)
    except requests.exceptions.Timeout:
        print("[llm_client] OpenRouter request timed out.")
        return generate_fallback_report(stats)
    except Exception as e:
        print(f"[llm_client] Exception during OpenRouter API call: {e}")
        return generate_fallback_report(stats)
