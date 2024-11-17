# app/models/payment.py

from sqlalchemy import Column, Integer, Float, Date, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    lease_id = Column(Integer, ForeignKey('leases.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=True)
    status = Column(String(20), default='Completed')
    notes = Column(Text, nullable=True)

    # Relationships
    lease = relationship('Lease', back_populates='payments')
