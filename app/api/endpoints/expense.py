# app/api/endpoints/expense.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=schemas.Expense)
async def create_expense(
    expense_in: schemas.ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        expense = await crud.crud_expense.create_expense(db=db, expense_in=expense_in, owner_id=current_user.id)
        return expense
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Expense])
async def read_expenses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = await crud.crud_expense.get_expenses(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return expenses

@router.get("/{expense_id}", response_model=schemas.Expense)
async def read_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = await crud.crud_expense.get_expense(db=db, expense_id=expense_id, owner_id=current_user.id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=schemas.Expense)
async def update_expense(
    expense_id: int,
    expense_in: schemas.ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = await crud.crud_expense.get_expense(db=db, expense_id=expense_id, owner_id=current_user.id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    try:
        updated_expense = await crud.crud_expense.update_expense(db=db, db_expense=expense, expense_in=expense_in)
        return updated_expense
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{expense_id}", response_model=schemas.Expense)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = await crud.crud_expense.delete_expense(db=db, expense_id=expense_id, owner_id=current_user.id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense
