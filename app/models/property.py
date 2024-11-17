# app/models/property.py

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.database import Base

class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Auto-incrementing primary key
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Foreign key to User model
    
    address = Column(String(255), nullable=False)
    num_bedrooms = Column(Integer, nullable=True)
    num_bathrooms = Column(Integer, nullable=True)
    num_floors = Column(Integer, nullable=True)
    is_commercial = Column(Boolean, default=False)
    is_hoa = Column(Boolean, default=False)
    hoa_fee = Column(Float, nullable=True)
    is_nnn = Column(Boolean, default=False)
    purchase_price = Column(Float, nullable=True)
    purchase_date = Column(Date, nullable=True)
    property_type = Column(String(50), nullable=True)
    
    # Relationships with lazy loading using 'selectin'
    owner = relationship('User', back_populates='properties', lazy='selectin')
    leases = relationship('Lease', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    expenses = relationship('Expense', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    incomes = relationship('Income', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    invoices = relationship('Invoice', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    contracts = relationship('Contract', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    documents = relationship('Document', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    tenants = relationship('Tenant', back_populates='property', lazy='selectin', cascade="all, delete-orphan")
    utilities = relationship('Utility', back_populates='property', lazy='selectin', cascade="all, delete-orphan")