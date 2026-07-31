from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# ---------- Skill ----------
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: Optional[str] = None
    current_level: int = Field(0, ge=0, le=100)
    target_level: int = Field(80, ge=0, le=100)
    priority: int = Field(3, ge=1, le=5)
    notes: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    category: Optional[str] = None
    current_level: Optional[int] = Field(None, ge=0, le=100)
    target_level: Optional[int] = Field(None, ge=0, le=100)
    priority: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class SkillRead(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Transaction ----------
class TransactionBase(BaseModel):
    skill_id: Optional[int] = None
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    currency: str = Field("INR", min_length=3, max_length=3)
    category: str = Field("learning", max_length=80)
    txn_date: date = Field(default_factory=date.today)          # ← renamed, no clash
    is_recurring: bool = False
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    skill_id: Optional[int] = None
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    category: Optional[str] = None
    txn_date: Optional[date] = None
    is_recurring: Optional[bool] = None
    notes: Optional[str] = None


class TransactionRead(TransactionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Analysis ----------
class AnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)
    job_description: str = Field(..., min_length=50)


class AnalysisRead(BaseModel):
    id: int
    resume_text: str
    job_description: str
    extracted_skills: Any
    gap_analysis: Any
    readiness_score: float
    ai_provider: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Learning Plan ----------
class LearningPlanCreate(BaseModel):
    analysis_id: Optional[int] = None
    title: str
    week_number: int = 1
    plan_json: str
    recommended_budget: float = 0.0
    total_hours: float = 0.0


class LearningPlanRead(LearningPlanCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Generic responses ----------
class Message(BaseModel):
    detail: str


class HealthCheck(BaseModel):
    status: str
    app: str
    version: str