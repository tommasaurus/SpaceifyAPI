# app/api/endpoints/payment.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=schemas.Payment)
async def create_payment(
    payment_in: schemas.PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        payment = await crud.crud_payment.create_payment(db=db, payment_in=payment_in, owner_id=current_user.id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Payment])
async def read_payments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payments = await crud.crud_payment.get_payments(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return payments

@router.get("/{payment_id}", response_model=schemas.Payment)
async def read_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = await crud.crud_payment.get_payment(db=db, payment_id=payment_id, owner_id=current_user.id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.put("/{payment_id}", response_model=schemas.Payment)
async def update_payment(
    payment_id: int,
    payment_in: schemas.PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = await crud.crud_payment.get_payment(db=db, payment_id=payment_id, owner_id=current_user.id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    try:
        updated_payment = await crud.crud_payment.update_payment(db=db, db_payment=payment, payment_in=payment_in)
        return updated_payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{payment_id}", response_model=schemas.Payment)
async def delete_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = await crud.crud_payment.delete_payment(db=db, payment_id=payment_id, owner_id=current_user.id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
