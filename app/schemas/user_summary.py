# app/schemas/user_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserSummary(BaseModel):
    id: int
    email: str
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
