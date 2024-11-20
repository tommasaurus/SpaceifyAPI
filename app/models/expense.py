# app/models/expense.py

from sqlalchemy import Column, Integer, Float, Date, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), unique=True, nullable=True)

    category = Column(String(50), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    receipt_url = Column(String(255), nullable=True)
    is_recurring = Column(Boolean, default=False)
    frequency = Column(String(20), nullable=True)
    bank_account = Column(String(100), nullable=True)  
    method = Column(String(50), nullable=True)  
    entity = Column(String(100), nullable=True) 

    # Relationships
    property = relationship('Property', back_populates='expenses')
    vendor = relationship('Vendor', back_populates='expenses')
    invoice = relationship('Invoice', back_populates='expense')
    documents = relationship('Document', back_populates='expense')
