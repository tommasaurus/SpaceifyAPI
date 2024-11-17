# app/schemas/invoice/invoice.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from app.schemas.invoice.invoice_item import InvoiceItem, InvoiceItemCreate

class InvoiceBase(BaseModel):
    property_id: int
    vendor_id: Optional[int] = None

    invoice_number: Optional[str] = None
    amount: float
    paid_amount: Optional[float] = 0.0
    remaining_balance: Optional[float] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[str] = 'Unpaid'
    description: Optional[str] = None
    line_items: Optional[List[InvoiceItemCreate]] = []

    model_config = ConfigDict(from_attributes=True, extra='allow')

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    vendor_id: Optional[int] = None
    invoice_number: Optional[str] = None
    amount: Optional[float] = None
    paid_amount: Optional[float] = None
    remaining_balance: Optional[float] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None
    line_items: Optional[List[InvoiceItemCreate]] = []

    model_config = ConfigDict(from_attributes=True, extra='allow')

class InvoiceInDBBase(InvoiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Invoice(InvoiceInDBBase):
    line_items: Optional[List[InvoiceItem]] = []  

    model_config = ConfigDict(from_attributes=True)
