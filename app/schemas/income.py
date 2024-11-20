# app/schemas/income.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from app.schemas.property_summary import PropertySummary

class IncomeBase(BaseModel):
    property_id: int
    category: Optional[str] = None
    amount: float
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    bank_account: Optional[str] = None  
    method: Optional[str] = None  
    entity: Optional[str] = None  

class IncomeCreate(IncomeBase):
    pass

class IncomeUpdate(BaseModel):
    property_id: Optional[int] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    bank_account: Optional[str] = None  
    method: Optional[str] = None  
    entity: Optional[str] = None  

class IncomeInDBBase(IncomeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Income(IncomeInDBBase):
    property: PropertySummary

    model_config = ConfigDict(from_attributes=True)
