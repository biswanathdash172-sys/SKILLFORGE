# SKILLFORGE

# SkillForge — AI Career + Finance Co-Pilot for Engineering Students

SkillForge helps engineering students answer three questions:

1. **Which skills** should I invest time and money in right now for the jobs I want?
2. **How much am I spending** on learning vs. the return I'm getting?
3. What's a **realistic weekly learning plan + budget** I can actually follow?

## Status

🚧 **In active development.** Backend is functional; frontend dashboard is not yet built.

| Layer                                       | Status         |
| ------------------------------------------- | -------------- |
| Skill CRUD API                              | ✅ Done        |
| Expense/Transaction tracker API             | ✅ Done        |
| Resume vs. JD gap analysis (AI-powered)     | ✅ Done        |
| Transparent readiness scoring               | ✅ Done        |
| Weekly learning plan generator              | ✅ Done        |
| PPTX one-click export                       | ✅ Done        |
| Frontend dashboard (HTML/Tailwind/Chart.js) | Demo is done    |

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + SQLite
- **Frontend:** HTML + Tailwind CSS + vanilla JS + Chart.js _(planned)_
- **AI:** Currently Groq (Llama 3.3 70B) — see note below
- **Export:** python-pptx
- **Config:** pydantic-settings + python-dotenv

> **Note on AI provider:** the original spec called for Claude or Gemini. The current implementation calls Groq's Llama model instead. This works and is free/fast, but if you want to stick to the original plan, swap `services/analysis.py` and `services/plan_generator.py` to use the `anthropic` or `google-generativeai` SDKs (both are already in `requirements.txt`).

## Project Structure

```
skillforge/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── database.py        # engine, session, settings
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── services/
│   │   │   ├── analysis.py        # resume/JD gap analysis via AI
│   │   │   ├── scoring.py         # transparent readiness score
│   │   │   ├── plan_generator.py  # weekly plan + budget
│   │   │   └── export.py          # PPTX export
│   │   └── routers/
│   │       ├── skills.py
│   │       ├── transactions.py
│   │       ├── analyze.py
│   │       └── plan.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/           # demo is there
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── ARCHITECTURE.md
├── LEARNINGS.md
└── README.md
```

## Setup

```bash
cd skillforge/backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your real API key(s) — NEVER commit this file

uvicorn app.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs` once running.

## API Overview

| Method       | Endpoint                       | Purpose                                          |
| ------------ | ------------------------------ | ------------------------------------------------ |
| `GET`        | `/health`                      | Health check                                     |
| `POST`       | `/skills/`                     | Create a skill                                   |
| `GET`        | `/skills/`                     | List skills                                      |
| `PUT/DELETE` | `/skills/{id}`                 | Update/delete a skill                            |
| `POST`       | `/transactions/`               | Log a learning expense                           |
| `GET`        | `/transactions/`               | List expenses (filterable by skill)              |
| `POST`       | `/analyze/`                    | Run resume vs. job-description gap analysis      |
| `POST`       | `/plan/generate/{analysis_id}` | Generate a weekly learning plan from an analysis |
| `GET`        | `/plan/{plan_id}/export`       | Download the plan as PPTX                        |

## Security Note

`backend/.env` must **never** be committed — it holds your real API key. Only `.env.example` (with placeholder values) belongs in git. If a real key was ever pushed to a public repo, treat it as compromised and rotate it immediately at your AI provider's console.

## Contributing / Working Notes


