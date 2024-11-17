# app/models/invoice/invoice.py

from sqlalchemy import Column, Integer, Float, Date, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True)

    invoice_number = Column(String(50), nullable=True)
    amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    remaining_balance = Column(Float, nullable=False)
    invoice_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(20), default='Unpaid')
    description = Column(Text, nullable=True)

    # Relationships
    property = relationship('Property', back_populates='invoices')
    vendor = relationship('Vendor', back_populates='invoices')
    expense = relationship('Expense', back_populates='invoice', uselist=False, cascade="all, delete-orphan")
    document = relationship('Document', back_populates='invoice', uselist=False, cascade="all, delete-orphan")
    line_items = relationship(
        'InvoiceItem',
        back_populates='invoice',
        cascade='all, delete-orphan',
        lazy='joined'  # Eagerly load line_items
    )
