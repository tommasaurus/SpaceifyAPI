# app/schemas/document.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.property_summary import PropertySummary
from app.schemas.lease_summary import LeaseSummary
from app.schemas.expense_summary import ExpenseSummary
from app.schemas.invoice.invoice_summary import InvoiceSummary
from app.schemas.contract_summary import ContractSummary

class DocumentBase(BaseModel):
    property_id: Optional[int] = None    
    lease_id: Optional[int] = None
    tenant_id: Optional[int] = None
    expense_id: Optional[int] = None
    invoice_id: Optional[int] = None
    contract_id: Optional[int] = None
    document_type: str    
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    property_id: Optional[int] = None    
    lease_id: Optional[int] = None
    tenant_id: Optional[int] = None
    expense_id: Optional[int] = None
    invoice_id: Optional[int] = None
    contract_id: Optional[int] = None
    document_type: Optional[str] = None    
    description: Optional[str] = None

class DocumentInDBBase(DocumentBase):
    id: int
    upload_date: datetime

    model_config = ConfigDict(from_attributes=True)

class Document(DocumentInDBBase):
    # property: Optional[PropertySummary] = None    
    # lease: Optional[LeaseSummary] = None
    # expense: Optional[ExpenseSummary] = None
    # invoice: Optional[InvoiceSummary] = None
    # contract: Optional[ContractSummary] = None

    model_config = ConfigDict(from_attributes=True)

class DocumentDeleteResponse(BaseModel):
    id: int
    message: str