import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response, jsonify
from config import SECRET_KEY, MIN_RECORDS
from core.upload import validate_csv
from core.analysis import run_analysis
from core.prompt_builder import build_prompt
from core.llm_client import generate_report
from core.report_builder import assemble_report
from core.exporter import export_pdf, export_txt

import config as _config

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Make config available to all templates (model name only — no secrets exposed)
@app.context_processor
def inject_config():
    return {'config': {
        'OPENROUTER_MODEL': _config.OPENROUTER_MODEL or 'AI Model',
    }}

DEMO_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'demo_data.csv')

import uuid

# In-memory storage for session data (avoids 4KB cookie size limit)
STORE = {}

def get_sid():
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    return session['sid']

# Storage helper (prefers Flask session serialized, falls back to STORE)
def get_user_store():
    sid = get_sid()
    store = STORE.get(sid)
    if not store:
        # Attempt to recover from Flask session cookie
        raw = session.get('user_store')
        if raw:
            try:
                store = json.loads(raw)
                STORE[sid] = store
            except Exception:
                store = {}
        else:
            store = {}
    return sid, store

def save_user_store(sid, store):
    STORE[sid] = store
    try:
        # Keep a JSON-encoded backup in Flask session cookie for serverless persistence
        session['user_store'] = json.dumps(store)
    except Exception as e:
        print(f"Session save warning: {e}")

def _nav_flags(sid):
    """Return breadcrumb enable flags based on what exists in user store for this session."""
    _, store = get_user_store()
    return {
        'has_stats': bool(store.get('stats')),
        'has_report': bool(store.get('report')),
    }

@app.route('/')
def index():
    sid, _ = get_user_store()
    return render_template('screen1_upload.html', active_screen=1, **_nav_flags(sid))

@app.route('/upload', methods=['POST'])
def upload():
    sid, _ = get_user_store()
    if 'file' not in request.files:
        return render_template('screen1_upload.html', active_screen=1,
                               errors=["No file selected. Please upload a CSV file."], **_nav_flags(sid))

    file = request.files['file']
    result = validate_csv(file)

    if not result['valid']:
        return render_template('screen1_upload.html', active_screen=1,
                               errors=result['errors'], warnings=result['warnings'], **_nav_flags(sid))

    store = {
        'validated_data': result['data'],
        'summary': result['summary'],
        'warnings': result['warnings']
    }
    save_user_store(sid, store)

    return render_template(
        'screen1_upload.html',
        active_screen=1,
        valid=True,
        summary=result['summary'],
        warnings=result['warnings'],
        **_nav_flags(sid)
    )

@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(app.root_path, 'static', 'favicon.ico'), mimetype='image/vnd.microsoft.icon')

@app.route('/use-demo', methods=['POST'])
def use_demo():
    sid, _ = get_user_store()
    if not os.path.exists(DEMO_CSV_PATH):
        return render_template('screen1_upload.html', active_screen=1,
                               errors=["Demo CSV file not found on server."], **_nav_flags(sid))

    with open(DEMO_CSV_PATH, 'rb') as f:
        class DummyFile:
            def __init__(self, fp):
                self.fp = fp
                self.filename = 'demo_data.csv'
            def read(self, *args, **kwargs):
                return self.fp.read(*args, **kwargs)
            def seek(self, *args, **kwargs):
                return self.fp.seek(*args, **kwargs)

        dummy = DummyFile(f)
        result = validate_csv(dummy)

    if not result['valid']:
        return render_template('screen1_upload.html', active_screen=1,
                               errors=result['errors'], **_nav_flags(sid))

    store = {
        'validated_data': result['data'],
        'summary': result['summary'],
        'warnings': result['warnings']
    }
    save_user_store(sid, store)

    return render_template(
        'screen1_upload.html',
        active_screen=1,
        valid=True,
        summary=result['summary'],
        warnings=result['warnings'],
        **_nav_flags(sid)
    )

@app.route('/analyse', methods=['POST'])
def analyse():
    sid, user_store = get_user_store()
    records = user_store.get('validated_data')
    if not records:
        return redirect(url_for('index'))

    stats = run_analysis(records)
    user_store['stats'] = stats
    save_user_store(sid, user_store)
    return render_template('screen2_analysis.html', active_screen=2, stats=stats, **_nav_flags(sid))

@app.route('/analyse-view', methods=['GET'])
def analyse_view():
    sid, user_store = get_user_store()
    stats = user_store.get('stats')
    if not stats:
        return redirect(url_for('index'))
    return render_template('screen2_analysis.html', active_screen=2, stats=stats, **_nav_flags(sid))

@app.route('/generate', methods=['POST'])
def generate():
    sid, user_store = get_user_store()
    stats = user_store.get('stats')
    summary_info = user_store.get('summary', {})

    if not stats:
        return redirect(url_for('index'))

    # Build prompt
    prompt = build_prompt(stats, summary_info)
    
    # Call OpenRouter LLM (or fallback)
    llm_result = generate_report(prompt, stats)
    
    # Assemble full report — pass summary_info for confidence scoring
    report_dict = assemble_report(stats, llm_result, summary_info)
    user_store['report'] = report_dict
    save_user_store(sid, user_store)

    return redirect(url_for('report_view'))

@app.route('/report', methods=['GET', 'POST'])
def report_view():
    sid, user_store = get_user_store()
    report_dict = user_store.get('report')
    if not report_dict:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Update optional Reporting Context fields
        report_dict['reporting_team'] = request.form.get('reporting_team', '').strip()
        report_dict['reporting_area'] = request.form.get('reporting_area', '').strip()
        report_dict['intended_recipient'] = request.form.get('intended_recipient', '').strip()
        report_dict['prepared_by'] = request.form.get('prepared_by', '').strip()
        user_store['report'] = report_dict
        save_user_store(sid, user_store)

        if request.form.get('action') == 'save_context':
            return render_template('screen3_report.html', active_screen=3, report=report_dict, context_saved=True, **_nav_flags(sid))

    return render_template('screen3_report.html', active_screen=3, report=report_dict, **_nav_flags(sid))

@app.route('/export-page', methods=['GET'])
def export_page():
    sid, user_store = get_user_store()
    report_dict = user_store.get('report')
    if not report_dict:
        return redirect(url_for('index'))
    return render_template('screen4_export.html', active_screen=4, report=report_dict, **_nav_flags(sid))

@app.route('/export/pdf', methods=['GET'])
def export_pdf_route():
    sid, user_store = get_user_store()
    report_dict = user_store.get('report')
    if not report_dict:
        return redirect(url_for('index'))

    pdf_bytes = export_pdf(report_dict)
    filename = f"hwc_report_{report_dict.get('month_year', 'draft').lower().replace(' ', '_')}.pdf"
    
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@app.route('/export/txt', methods=['GET'])
def export_txt_route():
    sid, user_store = get_user_store()
    report_dict = user_store.get('report')
    if not report_dict:
        return redirect(url_for('index'))

    txt_str = export_txt(report_dict)
    filename = f"hwc_report_{report_dict.get('month_year', 'draft').lower().replace(' ', '_')}.txt"
    
    return Response(
        txt_str,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@app.route('/clear')
def clear():
    sid = get_sid()
    STORE.pop(sid, None)
    session.clear()
    return redirect(url_for('index'))

# ── Chatbot API ──────────────────────────────────────────────────────────────
CHAT_SYSTEM_PROMPT = """You are WildGuard Assistant, an AI helper embedded in WildGuard Report AI — a tool that helps wildlife conservation field officers analyse human-wildlife conflict (HWC) incident data and generate monthly reports.

You help users with:
- Understanding how to use the application (upload, analysis, report generation, export)
- Interpreting their incident analysis results (species patterns, zone distributions, time-of-day patterns, resolution rates)
- Understanding responsible AI practices applied in the tool
- Questions about human-wildlife conflict concepts and conservation field reporting
- SDG 15 (Life on Land) and SDG 17 (Partnerships for the Goals) alignment in the context of this tool

Rules:
- Be concise, professional, and practical. Conservation officers are busy field professionals.
- Never invent incident data, statistics, or field facts not provided to you.
- If the user asks about their specific uploaded data, acknowledge you don't have access to it directly and suggest they refer to the Analysis page.
- Do not discuss topics unrelated to wildlife conservation, HWC reporting, this application, or sustainability.
- Keep responses under 200 words unless a detailed explanation is genuinely needed.
- When referencing application features, use their exact screen names: Upload (Screen 1), Incident Analysis (Screen 2), Report Review (Screen 3), Export & Share (Screen 4).
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get('message') or '').strip()
    history = data.get('history') or []  # [{role, content}, ...]

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    from config import OPENROUTER_API_KEY, OPENROUTER_MODEL
    import requests as _req
    import os as _os

    api_key = OPENROUTER_API_KEY.strip() if OPENROUTER_API_KEY else ''
    if not api_key:
        return jsonify({
            'reply': "I'm currently running in demo mode — the AI API key is not configured. "
                     "Add your OPENROUTER_API_KEY to .env to enable the assistant."
        })

    model = OPENROUTER_MODEL.strip() or 'google/gemini-2.5-flash:free'
    site_url = _os.environ.get('SITE_URL', 'http://localhost:5000')

    # Build message list: system + trimmed history (last 8 turns) + new message
    messages = [{'role': 'system', 'content': CHAT_SYSTEM_PROMPT}]
    for turn in history[-8:]:
        role = turn.get('role', 'user')
        content = (turn.get('content') or '').strip()
        if role in ('user', 'assistant') and content:
            messages.append({'role': role, 'content': content})
    messages.append({'role': 'user', 'content': user_message})

    try:
        resp = _req.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': site_url,
                'X-Title': 'WildGuard Report AI',
            },
            json={
                'model': model,
                'messages': messages,
                'temperature': 0.4,
                'max_tokens': 400,
            },
            timeout=60,
        )
        if resp.status_code == 200:
            body = resp.json()
            # OpenRouter can return HTTP 200 with an upstream error payload
            if body.get('error'):
                err_msg = body['error'].get('message', '')
                print(f'[chat] OpenRouter upstream error: {err_msg[:200]}')
                if 'rate' in err_msg.lower() or 'limit' in err_msg.lower() or 'exhausted' in err_msg.lower():
                    return jsonify({'reply': 'The AI model is temporarily busy. Please wait a moment and try again.'})
                return jsonify({'reply': 'The AI service returned an error. Please try again in a moment.'})
            choices = body.get('choices', [])
            if choices and choices[0].get('message', {}).get('content'):
                return jsonify({'reply': choices[0]['message']['content']})
            print(f'[chat] Unexpected response structure: {body}')
            return jsonify({'reply': 'Sorry, I received an unexpected response. Please try again.'})
        elif resp.status_code == 401:
            print('[chat] OpenRouter 401 — invalid API key.')
            return jsonify({'reply': 'The AI assistant is unavailable — API key issue. Please check your configuration.'})
        elif resp.status_code == 429:
            print('[chat] OpenRouter 429 — rate limit hit.')
            return jsonify({'reply': 'The AI assistant is temporarily rate-limited. Please wait a moment and try again.'})
        else:
            print(f'[chat] OpenRouter error {resp.status_code}: {resp.text[:200]}')
            return jsonify({'reply': 'Sorry, I could not reach the AI service right now. Please try again in a moment.'})
    except _req.exceptions.Timeout:
        print('[chat] OpenRouter request timed out.')
        return jsonify({'reply': 'The AI assistant timed out. Please try again.'})
    except Exception as exc:
        print(f'[chat] Exception: {exc}')
        return jsonify({'reply': 'Sorry, something went wrong. Please try again.'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
