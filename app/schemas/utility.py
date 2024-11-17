# app/schemas/utility.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class UtilityBase(BaseModel):    
    utility_type: str
    utility_cost: Optional[float] = 0
    company_name: str    
    account_number: Optional[str] = None
    contact_number: Optional[str] = None
    website: Optional[str] = None

class UtilityCreate(UtilityBase):
    pass

class UtilityUpdate(BaseModel):
    utility_type: Optional[str] = None
    utility_cost: Optional[float] = 0
    company_name: Optional[str] = None
    account_number: Optional[str] = None
    contact_number: Optional[str] = None
    website: Optional[str] = None

class UtilityInDBBase(UtilityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Utility(UtilityInDBBase):

    model_config = ConfigDict(from_attributes=True)
