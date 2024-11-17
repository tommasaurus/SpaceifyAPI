# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    profile_pic = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)  

    # Relationships
    properties = relationship('Property', back_populates='owner')
    vendors = relationship('Vendor', back_populates='owner')
    tenants = relationship('Tenant', back_populates='owner')  # Add this line
