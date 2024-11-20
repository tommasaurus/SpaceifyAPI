# app/models/income.py

from sqlalchemy import Column, Integer, Float, Date, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Income(Base):
    __tablename__ = 'incomes'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    category = Column(String(50), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    bank_account = Column(String(100), nullable=True)
    method = Column(String(50), nullable=True)  
    entity = Column(String(100), nullable=True)  

    # Relationships
    property = relationship('Property', back_populates='incomes')
