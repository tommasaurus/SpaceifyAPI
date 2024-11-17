from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import date
from .lease_summary import LeaseSummary
from .property_summary import PropertySummary

class TenantBase(BaseModel):
    property_id: Optional[int] = None
    lease_id: Optional[int] = None
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    landlord: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = 'current'

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    property_id: Optional[int] = None
    lease_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    landlord: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None

class TenantResponse(BaseModel):
    id: int
    owner_id: int
    property_id: Optional[int] = None
    lease_id: Optional[int] = None
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    landlord: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    lease: Optional[LeaseSummary] = None
    property: Optional[PropertySummary] = None

    model_config = ConfigDict(from_attributes=True)
