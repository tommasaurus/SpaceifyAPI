# app/schemas/income_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class IncomeSummary(BaseModel):
    id: int
    category: str
    amount: float
    date_received: date

    model_config = ConfigDict(from_attributes=True)
