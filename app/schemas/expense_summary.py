# app/schemas/expense_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class ExpenseSummary(BaseModel):
    id: int
    category: str
    amount: float
    date_incurred: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
