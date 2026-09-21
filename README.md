# 🌿 WildGuard Report AI
### AI-Powered Human-Wildlife Conflict (HWC) Incident Analysis & Standardised Reporting

> **1M1B AI for Sustainability Virtual Internship** — IBM SkillsBuild & AICTE  
> **Author**: Sivasubramaniyan G | sivasubramaniyan.g2511@gmail.com  
> **Primary SDG**: [SDG 15 — Life on Land](https://sdgs.un.org/goals/goal15) | **Secondary SDG**: [SDG 17 — Partnerships for the Goals](https://sdgs.un.org/goals/goal17)

---

## 📌 Executive Summary

**WildGuard Report AI** is a specialized web application designed for wildlife conservation monitoring teams, community conservancies, and field officers. It converts raw incident records (CSV) into standardized, professional monthly reports in under 2 minutes.

By automating statistical aggregation and AI narrative drafting, field officers can easily generate structured information-sharing documents that bridge the gap between ground-level monitoring teams, wildlife authorities, and conservation partners.

---

## 🎯 Key Features & Capabilities

- 📂 **CSV Data Upload & Validation**: Automatic column validation, date/time parsing, and cleaning of raw incident logs.
- 📊 **Automated Statistical Analysis**: Instant calculation of species distributions, zone hotspots, temporal (time-of-day) patterns, and resolution rates.
- 🤖 **Grounded AI Narrative Draft**: Generates an 8-section formal report draft using OpenRouter LLM API without hallucinating facts.
- 🤝 **Reporting Context & SDG 17 Integration**: Capture metadata (Reporting Team, Area, Intended Recipient, Prepared By) for standardized partner coordination.
- 🛡️ **Data Confidence Engine**: Evaluates dataset quality across volume, completeness, time coverage, and resolution tracking.
- 📄 **Multi-Format Export**: One-click download of executive PDF reports and plain-text files.
- 💬 **WildGuard Assistant Chatbot**: Built-in draggable AI assistant available on every screen for quick guidance.

---

## 🌍 SDG Alignment (Primary & Secondary)

| Goal | Contribution & Impact | Relevant Targets |
|---|---|---|
| **SDG 15 — Life on Land** *(Primary)* | Analyzes species pressure, territorial conflict zones, and incident trends to support biodiversity protection and anti-poaching patrol allocation. | **Target 15.5**: Protect natural habitats<br>**Target 15.7**: End poaching & trafficking |
| **SDG 17 — Partnerships for the Goals** *(Secondary)* | Generates standardized, shareable reports that enable structured data exchange and coordination between community monitors, wildlife authorities, and partners. | **Target 17.16**: Multi-stakeholder partnerships<br>**Target 17.18**: Quality, timely data capacity |

---

## 💡 1M1B Design Thinking & AI Tools Framework

### 1. Problem Statement
> *"How might we use AI to automate human-wildlife conflict incident pattern analysis and draft standardized reporting documents so that community monitoring teams and wildlife authorities can share timely, reliable data to protect biodiversity?"*

### 2. Design Thinking Process (Powered by IBM BOB)
- **Stage 1: Empathize (with IBM BOB)** — Used **IBM BOB** to explore the lived experiences of field officers and community monitors in remote conservancies, identifying their key pain points around manual paper/CSV parsing and delayed partner communication.
- **Stage 2: Define** — Formulated a clear target requirement: ground teams need a zero-setup tool to convert raw CSV logs into factual statistical patterns and reviewable draft reports.
- **Stage 3: Ideate (with IBM BOB)** — Brainstormed architectural solutions with **IBM BOB**, designing a hybrid approach combining deterministic Python aggregation (zero hallucination) with LLM narrative drafting.
- **Stage 4: Prototype (with IBM BOB)** — Used **IBM BOB** to guide the structural flow and UI component layout of the 4-screen web prototype (automated CSV validation, data confidence scoring, interactive dashboards, and standardized PDF export).
- **Stage 5: Test & Refine** — Refined responsible AI safeguards (disclaimers, small-sample flags, no false causation) and added optional *Reporting Context* metadata to enable SDG 17 information sharing.

### 3. AI Tools & Methodologies Used
- **IBM BOB** — Primary AI design thinking assistant utilized across the **Empathize**, **Ideate**, and **Prototype** stages to structure the problem, design the grounded AI architecture, and define responsible AI guardrails.
- **Prompt Engineering** — Designed a strict 8-section report prompt with explicit language constraints and small-sample warnings.
- **Grounded AI Architecture (RAG-Inspired)** — Python retrieves and aggregates statistics deterministically before narrative generation (preventing hallucinations).
- **OpenRouter REST API** — Powers fast, zero-cost report drafting via `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`.

---

## 🔄 User Workflow

```
[ 01 Upload ] ────► [ 02 Analysis ] ────► [ 03 Report Review ] ────► [ 04 Export & Share ]
  CSV Validation      KPI Dashboard         AI Narrative Draft         Standardized PDF/TXT
  Demo Data Option    Observed Patterns     Reporting Context Form     Partner-Ready Artifact
```

1. **Upload (`01 Upload`)**: Upload incident CSV or use synthetic demo data.
2. **Analysis (`02 Analysis`)**: View 5 key KPI summary cards, distribution tables, and automated pattern statements.
3. **Report (`03 Report Review`)**: Review AI draft, fill in optional *Reporting Context* fields, and inspect Data Confidence score.
4. **Export & Share (`04 Export & Share`)**: Download standardized PDF/TXT documents ready for organizational sharing.

---

## 🏗️ Technical Architecture

```
                       Browser (HTML5 / CSS3 / Vanilla JS)
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
  POST /upload                 POST /analyse               POST /generate
  (CSV Validation)          (Pandas Aggregation)         (Prompt → LLM)
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                               Flask Backend (app.py)
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
     core/upload.py          core/analysis.py          core/llm_client.py
    (Validation)            (Stats & Confidence)       (OpenRouter API)
                                                               │
                                                               ▼
                                                     core/exporter.py
                                                     (ReportLab PDF/TXT)
```

### Separation of Responsibilities:
- **Python Engine (`core/`)**: Validates data, calculates counts, percentages, confidence scores, and pattern statements.
- **LLM API (OpenRouter)**: Receives pre-calculated statistical summaries to write professional prose. *Never receives raw CSV files or private details.*

---

## 💻 Technology Stack

| Layer | Component | Technologies Used |
|---|---|---|
| **Backend** | Framework | Python 3.10+, Flask 3.x, python-dotenv |
| **Data & Logic** | Processing | Pandas 2.x, python-dateutil |
| **AI Integration** | LLM API | OpenRouter REST API (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`) |
| **Document Export**| PDF Engine | ReportLab 4.x |
| **Frontend** | UI & UX | Vanilla HTML5, Modern CSS3 (Glassmorphism & CSS Variables), JavaScript (ES6) |

---

## 🛡️ Responsible AI & Safety Framework

| Principle / Risk | Mitigation Built Into WildGuard Report AI |
|---|---|
| **Zero Hallucination** | LLM receives only pre-calculated Python statistics. It cannot invent numbers or incidents. |
| **No Causation Claims** | Prompt rules strictly prohibit inferring cause. Reports use qualified terms ("observed distribution"). |
| **Human Review Required** | Prominent disclaimer on all screens, drafts, and exported PDFs: *"AI-Generated Draft — Human Review Required"*. |
| **Small Sample Shield** | Datasets with < 20 records are automatically flagged to ensure cautious interpretation. |
| **Privacy First** | In-memory session processing (`STORE` dict). No database or external cloud storage. |
| **Graceful Fallback** | Full offline static fallback engine if the AI API is unavailable. |

---

## 📊 Data Confidence Score Algorithm

WildGuard Report AI evaluates uploaded dataset reliability out of 100 points:

| Evaluated Metric | Benchmark Criteria | Points |
|---|---|---|
| **Record Volume** | ≥ 50 records (High) / 20–49 (Moderate) / < 20 (Small) | 30 pts |
| **Time Coverage** | ≥ 90% valid timestamp entries | 25 pts |
| **Data Completeness** | 0% rows excluded during validation | 20 pts |
| **Resolution Tracking**| 0% records with 'Unknown' status | 15 pts |
| **Sample Sufficiency** | Sufficient count for statistical pattern analysis | 10 pts |

*Grade Scale: High (85–100) · Medium (60–84) · Low (0–59)*

---

## 📋 CSV File Specification

Uploaded CSV files must contain the following columns (case-insensitive):

| Column Name | Required | Type / Format | Example |
|---|---|---|---|
| `date` | ✅ Required | `YYYY-MM-DD` or `DD/MM/YYYY` | `2026-03-15` |
| `time` | ⚙ Optional | `HH:MM` (24-hr format) | `19:30` |
| `zone` | ✅ Required | Text / Patrol Zone Name | `Zone Alpha` |
| `species` | ✅ Required | Text / Wildlife Name | `Elephant` |
| `incident_type` | ✅ Required | Text / Conflict Category | `Crop Raid` |
| `damage_description`| ⚙ Optional | Free text | `Maize field entered` |
| `resolved` | ✅ Required | `Yes` / `No` / `1` / `0` | `No` |

*Limits: Minimum 5 valid records, maximum 5 MB file size.*

---

## 🛠️ Quickstart Guide

### 1. Clone & Set Up Environment
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/wildguard-report-ai.git
cd wildguard-report-ai

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the project root:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
SECRET_KEY=wildguard-secret-key-2026
```

### 3. Run Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## 📁 Repository Structure

```
1m1bproject/
├── app.py                      # Flask Application Routes & API endpoints
├── config.py                   # Configuration & Environment loading
├── requirements.txt            # Python dependencies
├── .env.example                # Template environment variables
├── core/
│   ├── upload.py               # CSV Validation & Cleaning
│   ├── analysis.py             # Statistical Engine & Quality Scoring
│   ├── prompt_builder.py       # Grounded LLM Prompt Construction
│   ├── llm_client.py           # OpenRouter API Integration & Fallbacks
│   ├── report_builder.py       # Report Dictionary Assembly
│   └── exporter.py             # ReportLab PDF & TXT Generation
├── templates/
│   ├── base.html               # Master Layout & Floating Chatbot Component
│   ├── screen1_upload.html     # Screen 1: File Upload & Demo Data
│   ├── screen2_analysis.html   # Screen 2: Analytics & KPI Dashboard
│   ├── screen3_report.html     # Screen 3: Draft Review & Context Form
│   └── screen4_export.html     # Screen 4: Export & Share
├── static/
│   ├── css/main.css            # Custom CSS Design System
│   └── js/app.js               # Dynamic UI Interactions & Chatbot Logic
└── data/
    ├── demo_data.csv           # Default synthetic dataset
    └── test_incidents.csv      # Sample test dataset
```

---

<div align="center">
  <sub>Built for the <b>1M1B AI for Sustainability Virtual Internship</b> with IBM SkillsBuild & AICTE.</sub>
</div>
