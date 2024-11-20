# app/schemas/expense_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class ExpenseSummary(BaseModel):
    id: int
    category: Optional[str] = None
    amount: float
    transaction_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
