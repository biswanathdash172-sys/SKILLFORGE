# LEARNINGS.md

A running log of what was learned/decided in each development phase.

## Phase: Backend Foundation (Skills, Transactions, Analysis, Plan, Export)

- Built FastAPI backend with SQLAlchemy 2.0 models: `Skill`, `Transaction`, `AnalysisResult`, `LearningPlan`.
- Implemented full CRUD for skills and transactions with duplicate-name and not-found handling.
- AI-powered resume-vs-JD gap analysis implemented using Groq (Llama 3.3 70B) instead of the originally planned Claude/Gemini — decision made for speed/cost during early development. Revisit before shipping if provider consistency matters.
- Built a transparent, explainable readiness scoring formula (coverage + level bonus − critical-skill penalty) instead of a black-box score, matching the "transparent scoring" requirement.
- Weekly learning plan generator has a solid mock fallback so the app still works if the AI call fails or the API key isn't set.
- PPTX export implemented with python-pptx and a proper slate/blue color palette.

### Bugs found & fixed

- `routers/plan.py` had `export_plan_pptx` defined twice on the same route — the second definition silently shadowed the first. Removed the duplicate.
- `backend/.env` (containing a real, live API key) had been committed to the public repo. Removed from git tracking with `git rm --cached`, added `.gitignore`, rotated the exposed key at the Groq console. Lesson: check `git status` and `.gitignore` _before_ the first commit on any new project, not after.
- `backend/skillforge.db` (the SQLite database file) was also committed by mistake. Untracked it the same way — binary DB files don't belong in git for a project like this.

## Phase: Frontend Dashboard

- Built a 5-page frontend (`About`, `Skills`, `Expenses`, `Gap Analysis`, `Weekly Plan`) with a persistent sidebar nav, corporate/fintech visual style (navy + teal, Space Grotesk + Inter), and vanilla JS talking directly to the FastAPI backend — no framework needed for this scale.
- Used a shared `js/sidebar.js` and `js/api.js` across all pages instead of duplicating fetch/error-handling logic per page — one bug fix in `api.js` automatically applied everywhere.
- Chart.js (via CDN) used for the "spend by skill" doughnut chart on the Expenses page — pulled in only where a visual actually adds value over a table.
- Confirmed CORS already allowed `null` origin in `main.py`, so the frontend works when opened directly via `file://` without needing a local dev server.

### Bugs found & fixed

- `AnalysisRequest` in `schemas.py` enforces a 50-character minimum on `resume_text` and `job_description`, but the frontend didn't validate this client-side — users would've hit a raw 422 error with no clear message. Added a client-side length check with a clear toast message instead.
- FastAPI's 422 validation errors return `detail` as a **list** of `{loc, msg, type}` objects, not a plain string, but `api.js`'s error handler assumed a string. Fixed to handle both shapes so validation errors show a readable message instead of `[object Object]`.
- File naming mismatch: the Skills page was saved as `skill.html` (singular) while every sidebar link pointed to `skills.html` (plural), silently breaking navigation. Renamed with `git mv` to match. Lesson: verify every nav link actually resolves before considering a page "done," not just that the page itself loads.

### Next phase

- Manually test the full flow end to end: add a skill → log an expense → run a gap analysis → generate a weekly plan → export PPTX — and note anything that breaks here.
- Decide on the AI provider question (stay on Groq vs. switch to Claude/Gemini as originally planned) and update `ARCHITECTURE.md` + README to reflect the final decision, not a stale "planned" note.
- Consider adding basic frontend input validation feedback (e.g. inline field errors) rather than relying solely on toast messages, once the core flow is confirmed stable.
