from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=schemas.TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(txn_in: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Optional: verify the skill exists if skill_id is provided
    if txn_in.skill_id is not None:
        skill = db.query(models.Skill).filter(models.Skill.id == txn_in.skill_id).first()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with id {txn_in.skill_id} not found",
            )

    transaction = models.Transaction(**txn_in.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/", response_model=List[schemas.TransactionRead])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    skill_id: Optional[int] = Query(None, description="Filter by skill"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Transaction)
    if skill_id is not None:
        query = query.filter(models.Transaction.skill_id == skill_id)
    return query.order_by(models.Transaction.txn_date.desc()).offset(skip).limit(limit).all()


@router.get("/{txn_id}", response_model=schemas.TransactionRead)
def get_transaction(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn


@router.put("/{txn_id}", response_model=schemas.TransactionRead)
def update_transaction(
    txn_id: int, txn_in: schemas.TransactionUpdate, db: Session = Depends(get_db)
):
    txn = db.query(models.Transaction).filter(models.Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    update_data = txn_in.model_dump(exclude_unset=True)

    # Validate skill if it is being changed
    if "skill_id" in update_data and update_data["skill_id"] is not None:
        skill = db.query(models.Skill).filter(models.Skill.id == update_data["skill_id"]).first()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with id {update_data['skill_id']} not found",
            )

    for field, value in update_data.items():
        setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(txn)
    db.commit()
    return None