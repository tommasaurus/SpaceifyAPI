# app/schemas/tenant_summary.py

from pydantic import BaseModel, ConfigDict

class TenantSummary(BaseModel):
    id: int
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)
