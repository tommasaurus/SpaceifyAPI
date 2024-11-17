# app/schemas/document_summary.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DocumentSummary(BaseModel):
    id: int
    document_type: str    
    upload_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)