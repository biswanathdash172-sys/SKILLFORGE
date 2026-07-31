from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Float, Integer, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    current_level: Mapped[int] = mapped_column(Integer, default=0)
    target_level: Mapped[int] = mapped_column(Integer, default=80)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    transactions = relationship("Transaction", back_populates="skill", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("skills.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    category: Mapped[str] = mapped_column(String(80), default="learning")
    txn_date: Mapped[date] = mapped_column(Date, default=date.today)          # ← renamed
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill", back_populates="transactions")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_skills: Mapped[str] = mapped_column(Text, nullable=False)
    gap_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_provider: Mapped[str] = mapped_column(String(20), default="claude")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analysis_results.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, default=1)
    plan_json: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_budget: Mapped[float] = mapped_column(Float, default=0.0)
    total_hours: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)