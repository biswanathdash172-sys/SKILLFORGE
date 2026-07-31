# SkillForge Architecture

## Vision

Help engineering students answer:

1. Which skills should I invest time & money in right now?
2. How much am I spending on learning vs the return?
3. Give me a realistic weekly plan + budget I can actually follow.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 + SQLite (switchable to PostgreSQL)
- **Frontend**: HTML + Tailwind CSS + vanilla JS + Chart.js (upgrade path to Next.js)
- **AI**: Anthropic Claude or Google Gemini (provider switch via env)
- **Export**: python-pptx
- **Config**: pydantic-settings + python-dotenv

## Folder Structure

skillforge/
├── backend/
│ ├── app/
│ │ ├── init.py
│ │ ├── main.py # FastAPI entry
│ │ ├── database.py # engine, session, settings
│ │ ├── models.py # SQLAlchemy models
│ │ ├── schemas.py # Pydantic schemas
│ │ ├── services/ # business logic
│ │ │ ├── analysis.py
│ │ │ ├── scoring.py
│ │ │ ├── plan_generator.py
│ │ │ └── export.py
│ │ └── routers/ # API endpoints
│ │ ├── analyze.py
│ │ ├── transactions.py
│ │ ├── skills.py
│ │ └── plan.py
│ ├── requirements.txt
│ └── .env.example
├── frontend/
│ ├── index.html
│ ├── css/
│ ├── js/
│ └── assets/
├── LEARNINGS.md
├── ARCHITECTURE.md
└── README.md
