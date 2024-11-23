# app/api/endpoints/income.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=schemas.Income)
async def create_income(
    income_in: schemas.IncomeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        income = await crud.crud_income.create_income(db=db, income_in=income_in, owner_id=current_user.id)
        return income
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Income])
async def read_incomes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incomes = await crud.crud_income.get_incomes(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return incomes

@router.get("/{income_id}", response_model=schemas.Income)
async def read_income(
    income_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = await crud.crud_income.get_income(db=db, income_id=income_id, owner_id=current_user.id)
    if income is None:
        raise HTTPException(status_code=404, detail="Income not found")
    return income

@router.put("/{income_id}", response_model=schemas.Income)
async def update_income(
    income_id: int,
    income_in: schemas.IncomeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    income = await crud.crud_income.get_income(db=db, income_id=income_id, owner_id=current_user.id)
    if income is None:
        raise HTTPException(status_code=404, detail="Income not found")
    try:
        updated_income = await crud.crud_income.update_income(db=db, db_income=income, income_in=income_in)
        return updated_income
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{income_id}")
async def delete_income(
    income_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Modified to return a success message instead of the deleted object"""
    deleted = await crud.crud_income.delete_income(db=db, income_id=income_id, owner_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income successfully deleted"}
