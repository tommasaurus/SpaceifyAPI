# app/schemas/contract.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List, Any
from datetime import date
from app.schemas.property_summary import PropertySummary
from app.schemas.vendor_summary import VendorSummary

class ContractBase(BaseModel):
    property_id: int
    vendor_id: Optional[int] = None
    contract_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    terms: Optional[Dict[str, Any]] = None  # Changed to Any for nested JSON
    parties_involved: Optional[List[Dict[str, Any]]] = None  # List of parties as dicts
    is_active: Optional[bool] = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    property_id: Optional[int] = None
    vendor_id: Optional[int] = None
    contract_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    terms: Optional[Dict[str, Any]] = None
    parties_involved: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

class ContractInDBBase(ContractBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  

class Contract(ContractInDBBase):
    property: PropertySummary
    vendor: Optional[VendorSummary] = None

    model_config = ConfigDict(from_attributes=True)  
