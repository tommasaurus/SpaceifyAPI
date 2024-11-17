# app/schemas/payment_summary.py

from pydantic import BaseModel, ConfigDict
from datetime import date

class PaymentSummary(BaseModel):
    id: int
    amount: float
    payment_date: date
    due_date: date
    status: str

    model_config = ConfigDict(from_attributes=True)
