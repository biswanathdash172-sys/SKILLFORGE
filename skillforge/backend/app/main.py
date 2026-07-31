from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base, get_settings
from app.schemas import HealthCheck
from app.routers import skills, transactions, analyze, plan

settings = get_settings()

# backend/app/main.py -> backend/app -> backend -> skillforge -> skillforge/frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SkillForge API",
    description="AI Career + Finance Co-Pilot for Engineering Students",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status", response_model=HealthCheck)
def api_status():
    return HealthCheck(status="ok", app="SkillForge", version="0.1.0")


@app.get("/health", response_model=HealthCheck)
def health():
    return HealthCheck(status="healthy", app="SkillForge", version="0.1.0")


# Register all routers
app.include_router(skills.router)
app.include_router(transactions.router)
app.include_router(analyze.router)
app.include_router(plan.router)


# ---------------------------------------------------------------------------
# Serve the frontend (single-file HTML app) from the same process/port.
# Registered LAST so it never shadows the API routes above.
# ---------------------------------------------------------------------------
@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")