# app/crud/crud_payment.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.payment import Payment
from app.models.lease import Lease
from app.models.property import Property
from app.schemas.payment import PaymentCreate, PaymentUpdate

class CRUDPayment:
    async def get_payment(self, db: AsyncSession, payment_id: int, owner_id: int) -> Optional[Payment]:
        result = await db.execute(
            select(Payment)
            .join(Lease)
            .join(Property)
            .filter(Payment.id == payment_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_payments(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
        result = await db.execute(
            select(Payment)
            .join(Lease)
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_payment(self, db: AsyncSession, payment_in: PaymentCreate, owner_id: int) -> Payment:
        # Verify that the lease exists and belongs to a property owned by the user
        result = await db.execute(
            select(Lease)
            .join(Property)
            .filter(Lease.id == payment_in.lease_id)
            .filter(Property.owner_id == owner_id)
        )
        lease = result.scalars().first()
        if not lease:
            raise ValueError("Lease not found or you do not have permission to access this lease.")

        db_payment = Payment(**payment_in.dict())
        db.add(db_payment)
        try:
            await db.commit()
            await db.refresh(db_payment)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the payment: " + str(e))
        return db_payment

    async def update_payment(self, db: AsyncSession, db_payment: Payment, payment_in: PaymentUpdate) -> Payment:
        update_data = payment_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_payment, key, value)
        try:
            await db.commit()
            await db.refresh(db_payment)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the payment: " + str(e))
        return db_payment

    async def delete_payment(self, db: AsyncSession, payment_id: int, owner_id: int) -> Optional[Payment]:
        db_payment = await self.get_payment(db, payment_id, owner_id)
        if db_payment:
            await db.delete(db_payment)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the payment: " + str(e))
        return db_payment

# Initialize the CRUD object
crud_payment = CRUDPayment()
