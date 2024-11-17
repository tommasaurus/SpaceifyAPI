# app/schemas/lease_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class LeaseSummary(BaseModel):
    id: int
    lease_type: str
    rent_amount_monthly: Optional[float] = None    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
