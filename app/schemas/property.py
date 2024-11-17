# app/schemas/property.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from app.schemas.user_summary import UserSummary
from app.schemas.lease_summary import LeaseSummary
from app.schemas.expense_summary import ExpenseSummary
from app.schemas.income_summary import IncomeSummary
from app.schemas.invoice.invoice_summary import InvoiceSummary
from app.schemas.contract_summary import ContractSummary
from app.schemas.document_summary import DocumentSummary
from app.schemas.utility_summary import UtilitySummary  # Updated import

class PropertyBase(BaseModel):    
    address: str
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    num_floors: Optional[int] = None
    is_commercial: Optional[bool] = False
    is_hoa: Optional[bool] = False
    hoa_fee: Optional[float] = None
    is_nnn: Optional[bool] = False
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None
    property_type: Optional[str] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseModel):
    address: Optional[str] = None
    num_bedrooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    num_floors: Optional[int] = None
    is_commercial: Optional[bool] = None
    is_hoa: Optional[bool] = None
    hoa_fee: Optional[float] = None
    is_nnn: Optional[bool] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None
    property_type: Optional[str] = None

class PropertyInDBBase(PropertyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Property(PropertyInDBBase):
    owner: UserSummary    
    leases: Optional[List[LeaseSummary]] = []
    expenses: Optional[List[ExpenseSummary]] = []
    incomes: Optional[List[IncomeSummary]] = []
    invoices: Optional[List[InvoiceSummary]] = []
    contracts: Optional[List[ContractSummary]] = []
    documents: Optional[List[DocumentSummary]] = []
    utilities: Optional[List[UtilitySummary]] = []  # Added Utilities relationship

    model_config = ConfigDict(from_attributes=True)
