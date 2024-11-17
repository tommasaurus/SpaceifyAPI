# app/schemas/utility_summary.py

from pydantic import BaseModel, ConfigDict

class UtilitySummary(BaseModel):
    id: int
    utility_type: str
    company_name: str

    model_config = ConfigDict(from_attributes=True)
