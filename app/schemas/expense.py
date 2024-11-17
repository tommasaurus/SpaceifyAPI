# app/schemas/expense.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from app.schemas.property_summary import PropertySummary
from app.schemas.vendor_summary import VendorSummary

class ExpenseBase(BaseModel):
    property_id: int
    vendor_id: Optional[int] = None
    category: str
    amount: float
    date_incurred: Optional[date] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    is_recurring: Optional[bool] = False
    frequency: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    property_id: Optional[int] = None
    vendor_id: Optional[int] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    date_incurred: Optional[date] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    is_recurring: Optional[bool] = None
    frequency: Optional[str] = None

class ExpenseInDBBase(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Expense(ExpenseInDBBase):
    property: PropertySummary
    vendor: Optional[VendorSummary] = None

    model_config = ConfigDict(from_attributes=True)
