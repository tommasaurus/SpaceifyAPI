# app/schemas/payment.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from app.schemas.lease_summary import LeaseSummary

class PaymentBase(BaseModel):
    lease_id: int
    amount: float
    payment_date: date
    due_date: date
    payment_method: Optional[str] = None
    status: Optional[str] = 'Completed'
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class PaymentInDBBase(PaymentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Payment(PaymentInDBBase):
    lease: LeaseSummary

    model_config = ConfigDict(from_attributes=True)
