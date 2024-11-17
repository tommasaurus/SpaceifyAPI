# app/schemas/lease.py

from pydantic import BaseModel, ConfigDict, Extra
from typing import Optional, List, Dict, Any
from datetime import date

class LeaseBase(BaseModel):
    property_id: int

    lease_type: str
    description:Optional[str] = None
    rent_amount_total: Optional[float] = None
    rent_amount_monthly: Optional[float] = None
    security_deposit_amount: Optional[str] = "Not specified in extract"
    security_deposit_held_by: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    payment_frequency: Optional[str] = 'Monthly'
    tenant_info: Optional[Dict[str, Any]] = None  # Dictionary to hold tenant information
    special_lease_terms: Optional[Dict[str, Any]] = None  # JSON for special lease terms
    is_active: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True, extra='allow')     

class LeaseCreate(LeaseBase):
    pass

class LeaseUpdate(BaseModel):
    lease_type: Optional[str] = None
    description:Optional[str] = None
    rent_amount_total: Optional[float] = None
    rent_amount_monthly: Optional[float] = None
    security_deposit_amount: Optional[str] = None
    security_deposit_held_by: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    payment_frequency: Optional[str] = None
    tenant_info: Optional[Dict[str, Any]] = None
    special_lease_terms: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, extra='allow')

class LeaseInDBBase(LeaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Lease(LeaseInDBBase):
    model_config = ConfigDict(from_attributes=True)
