from datetime import datetime, timezone
from core.analysis import compute_confidence

RESPONSIBLE_AI_NOTICE = """AI-GENERATED DRAFT — HUMAN REVIEW REQUIRED

This report was prepared using automated pattern analysis and AI-assisted narrative generation. All observations are based solely on the uploaded incident records for the stated reporting period. Suggested mitigation considerations are not directives and do not constitute official guidance. The reviewing officer must validate all content against local field knowledge before submission to any wildlife authority or conservation organisation."""

def assemble_report(stats, llm_result, summary_info=None):
    confidence = compute_confidence(stats, summary_info or {})
    report_dict = {
        'period_formatted': stats.get('period_formatted', ''),
        'month_year': stats.get('month_year', ''),
        'total_records': stats.get('total_records', 0),
        'timed_records': stats.get('timed_records', 0),
        'small_sample': stats.get('small_sample', False),
        'llm_text': llm_result.get('text', ''),
        'is_demo': llm_result.get('is_demo', True),
        'model_used': llm_result.get('model_used', 'Fallback Engine'),
        'notice': RESPONSIBLE_AI_NOTICE,
        'stats': stats,
        'generated_at': datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC'),
        'confidence': confidence,
    }
    return report_dict
