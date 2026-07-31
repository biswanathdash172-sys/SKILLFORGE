from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app import models, schemas
from app.services.analysis import analyze_resume_and_jd

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("/", response_model=schemas.AnalysisRead, status_code=status.HTTP_201_CREATED)
def create_analysis(payload: schemas.AnalysisRequest, db: Session = Depends(get_db)):
    # Call Claude
    result = analyze_resume_and_jd(payload.resume_text, payload.job_description)

    # Store in database
    analysis = models.AnalysisResult(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
        extracted_skills=json.dumps(result.get("extracted_skills", {})),
        gap_analysis=json.dumps(result.get("gap_analysis", {})),
        readiness_score=float(result.get("readiness_score", 0)),
        ai_provider="groq",
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Convert JSON strings back to objects for the response
    return schemas.AnalysisRead(
        id=analysis.id,
        resume_text=analysis.resume_text,
        job_description=analysis.job_description,
        extracted_skills=json.loads(analysis.extracted_skills),
        gap_analysis=json.loads(analysis.gap_analysis),
        readiness_score=analysis.readiness_score,
        ai_provider=analysis.ai_provider,
        created_at=analysis.created_at,
    )


@router.get("/{analysis_id}", response_model=schemas.AnalysisRead)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(models.AnalysisResult).filter(models.AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    return schemas.AnalysisRead(
        id=analysis.id,
        resume_text=analysis.resume_text,
        job_description=analysis.job_description,
        extracted_skills=json.loads(analysis.extracted_skills),
        gap_analysis=json.loads(analysis.gap_analysis),
        readiness_score=analysis.readiness_score,
        ai_provider=analysis.ai_provider,
        created_at=analysis.created_at,
    )


@router.get("/", response_model=list[schemas.AnalysisRead])
def list_analyses(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(models.AnalysisResult)
        .order_by(models.AnalysisResult.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    results = []
    for analysis in rows:
        results.append(
            schemas.AnalysisRead(
                id=analysis.id,
                resume_text=analysis.resume_text,
                job_description=analysis.job_description,
                extracted_skills=json.loads(analysis.extracted_skills),
                gap_analysis=json.loads(analysis.gap_analysis),
                readiness_score=analysis.readiness_score,
                ai_provider=analysis.ai_provider,
                created_at=analysis.created_at,
            )
        )
    return results