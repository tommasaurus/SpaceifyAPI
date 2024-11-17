# app/models/tenant.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Tenant(Base):
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    property_id = Column(Integer, ForeignKey('properties.id', ondelete='CASCADE'), nullable=True)
    lease_id = Column(Integer, ForeignKey('leases.id', ondelete='CASCADE'), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    landlord = Column(String, nullable=True)
    address = Column(String, nullable=True)
    status = Column(String, default='current', nullable=False)

    # Define relationships with cascade
    property = relationship("Property", back_populates="tenants")
    lease = relationship("Lease", back_populates="tenants")
    owner = relationship("User", back_populates="tenants")