import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def export_txt(report_dict):
    output = []
    output.append("================================================================================")
    output.append("WildGuard Report AI — Monthly Human-Wildlife Conflict Incident Report")
    output.append("================================================================================")
    output.append(f"Reporting Period: {report_dict.get('period_formatted', '')}")
    output.append(f"Data Coverage: Based on {report_dict.get('total_records', 0)} valid incident records.")
    output.append(f"Status: {'[DEMO MODE]' if report_dict.get('is_demo') else '[LIVE AI DRAFT]'}")
    output.append("================================================================================\n")
    
    output.append("--- RESPONSIBLE AI NOTICE ---")
    output.append(report_dict.get('notice', ''))
    output.append("-----------------------------\n")
    
    output.append(report_dict.get('llm_text', ''))
    
    return "\n".join(output)

def format_pdf_text(text):
    """Safely convert markdown bolding to valid HTML tags for ReportLab and escape XML characters."""
    if not text:
        return ""
    # Escape XML characters for ReportLab compatibility
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Process double asterisks **bold** to <b>bold</b>
    parts = text.split('**')
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(f"<b>{part}</b>")
        else:
            out.append(part)
    res = "".join(out)
    return res.replace('*', '')

def export_pdf(report_dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    context_style = ParagraphStyle(
        'ContextBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=1,
        borderPadding=10,
        spaceAfter=15
    )

    notice_style = ParagraphStyle(
        'NoticeBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#873800'),
        backColor=colors.HexColor('#FFFBE6'),
        borderColor=colors.HexColor('#FFE58F'),
        borderWidth=1,
        borderPadding=10,
        spaceAfter=15
    )

    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#166534'),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    note_style = ParagraphStyle(
        'InfoSharingNote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor('#475569'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=1,
        borderPadding=10,
        spaceBefore=20
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("WildGuard Report AI", title_style))
    story.append(Paragraph("Human-Wildlife Conflict Reporting & Pattern Analysis", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#166534'), spaceAfter=12))

    # Reporting Context Metadata Block
    ctx_lines = []
    if report_dict.get('reporting_team'):
        ctx_lines.append(f"<b>Reporting Team:</b> {format_pdf_text(report_dict['reporting_team'])}")
    if report_dict.get('reporting_area'):
        ctx_lines.append(f"<b>Reporting Area:</b> {format_pdf_text(report_dict['reporting_area'])}")
    ctx_lines.append(f"<b>Reporting Period:</b> {format_pdf_text(report_dict.get('period_formatted', ''))}")
    if report_dict.get('intended_recipient'):
        ctx_lines.append(f"<b>Intended Recipient / Partner:</b> {format_pdf_text(report_dict['intended_recipient'])}")
    if report_dict.get('prepared_by'):
        ctx_lines.append(f"<b>Prepared By:</b> {format_pdf_text(report_dict['prepared_by'])}")

    context_html = "<br/>".join(ctx_lines)
    story.append(Paragraph(context_html, context_style))

    # Responsible AI Notice
    notice_text = f"<b>RESPONSIBLE AI NOTICE — HUMAN REVIEW REQUIRED</b><br/>{format_pdf_text(report_dict.get('notice', ''))}"
    story.append(Paragraph(notice_text, notice_style))

    # Body sections from LLM text
    llm_text = report_dict.get('llm_text', '')
    lines = llm_text.split('\n')

    for line in lines:
        line_str = line.strip()
        if not line_str or 'HUMAN REVIEW REQUIRED' in line_str.upper():
            continue

        # Strip markdown heading markers (## / # prefix from some models)
        line_clean = line_str.lstrip('#').strip()

        if not line_clean:
            continue

        if line_clean.startswith('---') or line_clean.startswith('==='):
            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
        elif 'SECTION' in line_clean.upper() and len(line_clean) < 80:
            clean_sec = format_pdf_text(line_clean)
            story.append(Paragraph(clean_sec, section_heading_style))
        elif line_clean.startswith('-') or line_clean.startswith('•') or (line_clean.startswith('*') and not line_clean.startswith('**')):
            clean_bullet = format_pdf_text(line_clean[1:].strip())
            story.append(Paragraph(f"• {clean_bullet}", bullet_style))
        else:
            clean_body = format_pdf_text(line_clean)
            story.append(Paragraph(clean_body, body_style))

    # Bottom Information Sharing Note
    info_note_text = "<b>Information-sharing note</b><br/>This report summarizes recorded incident data for the stated reporting period. It is intended to support communication and coordination between community monitoring teams and relevant conservation stakeholders. Findings should be reviewed by responsible personnel before operational decisions are made."
    story.append(Paragraph(info_note_text, note_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
