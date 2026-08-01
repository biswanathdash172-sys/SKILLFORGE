from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
from typing import List

from app.database import get_db
from app import models, schemas
from app.services.scoring import calculate_readiness_score
from app.services.plan_generator import generate_weekly_plan
from app.services.export import create_plan_pptx

router = APIRouter(prefix="/plan", tags=["Learning Plan"])


@router.post("/generate/{analysis_id}", response_model=schemas.LearningPlanRead, status_code=status.HTTP_201_CREATED)
def generate_plan_from_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(models.AnalysisResult).filter(models.AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    extracted = json.loads(analysis.extracted_skills)
    matching = extracted.get("matching_skills", [])
    missing = extracted.get("missing_skills", [])

    score_data = calculate_readiness_score(matching, missing)
    score = score_data["score"]

    plan_data = generate_weekly_plan(missing, score)

    plan = models.LearningPlan(
        analysis_id=analysis.id,
        title=plan_data.get("title", "Weekly Learning Plan"),
        week_number=plan_data.get("duration_weeks", 1),
        plan_json=json.dumps(plan_data),
        recommended_budget=float(plan_data.get("recommended_budget_inr", 0)),
        total_hours=float(plan_data.get("total_hours", 0)),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return schemas.LearningPlanRead(
        id=plan.id,
        analysis_id=plan.analysis_id,
        title=plan.title,
        week_number=plan.week_number,
        plan_json=plan.plan_json,
        recommended_budget=plan.recommended_budget,
        total_hours=plan.total_hours,
        created_at=plan.created_at,
    )


@router.get("/", response_model=List[schemas.LearningPlanRead])
def list_plans(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(models.LearningPlan)
        .order_by(models.LearningPlan.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{plan_id}", response_model=schemas.LearningPlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.LearningPlan).filter(models.LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_200_OK, response_model=schemas.Message)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.LearningPlan).filter(models.LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    db.delete(plan)
    db.commit()
    return schemas.Message(detail=f"Plan {plan_id} deleted")


@router.get("/{plan_id}/export")
def export_plan_pptx(plan_id: int, db: Session = Depends(get_db)):
    """
    One-click download of the learning plan as a professional PPTX.
    """
    plan = db.query(models.LearningPlan).filter(models.LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    try:
        buffer = create_plan_pptx(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PPTX: {str(e)}",
        )

    filename = f"SkillForge_Plan_{plan_id}.pptx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )