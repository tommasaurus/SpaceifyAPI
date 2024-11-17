# app/schemas/property_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class PropertySummary(BaseModel):
    id: int
    address: str
    property_type: Optional[str] = None
    is_commercial: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
