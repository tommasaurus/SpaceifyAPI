# app/models/contract.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True)
    contract_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(String(255), nullable=True)
    terms = Column(JSONB, nullable=True)
    parties_involved = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships with cascade
    property = relationship('Property', back_populates='contracts')
    vendor = relationship('Vendor', back_populates='contracts')
    document = relationship('Document', uselist=False, back_populates='contract', cascade="all, delete-orphan")