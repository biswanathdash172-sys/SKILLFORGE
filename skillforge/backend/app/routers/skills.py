from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("/", response_model=schemas.SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(skill_in: schemas.SkillCreate, db: Session = Depends(get_db)):
    # Check for duplicate name
    existing = db.query(models.Skill).filter(models.Skill.name == skill_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill with name '{skill_in.name}' already exists",
        )

    skill = models.Skill(**skill_in.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/", response_model=List[schemas.SkillRead])
def list_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Skill).offset(skip).limit(limit).all()


@router.get("/{skill_id}", response_model=schemas.SkillRead)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return skill


@router.put("/{skill_id}", response_model=schemas.SkillRead)
def update_skill(skill_id: int, skill_in: schemas.SkillUpdate, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    update_data = skill_in.model_dump(exclude_unset=True)

    # Prevent renaming to an existing name
    if "name" in update_data:
        existing = (
            db.query(models.Skill)
            .filter(models.Skill.name == update_data["name"], models.Skill.id != skill_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Skill with name '{update_data['name']}' already exists",
            )

    for field, value in update_data.items():
        setattr(skill, field, value)

    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")

    db.delete(skill)
    db.commit()
    return None