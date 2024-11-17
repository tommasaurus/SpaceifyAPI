# app/schemas/vendor_summary.py

from pydantic import BaseModel, ConfigDict

class VendorSummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
