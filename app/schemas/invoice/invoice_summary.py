# app/schemas/invoice_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class InvoiceSummary(BaseModel):
    id: int
    invoice_number: Optional[str] = None
    amount: float
    invoice_date: Optional[date] = None
    status: str

    model_config = ConfigDict(from_attributes=True, extra='allow')
