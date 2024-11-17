# app/models/utility.py

from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class Utility(Base):
    __tablename__ = 'utilities'

    id = Column(Integer, primary_key=True, index=True)
    
    utility_type = Column(String(50), nullable=False)
    utility_cost = Column(Float, nullable=True)
    company_name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=True)
    contact_number = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)

    # Foreign key linking directly to Property
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)

    # Relationships
    property = relationship('Property', back_populates='utilities')
