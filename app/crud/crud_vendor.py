# app/crud/crud_vendor.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate

class CRUDVendor:
    async def get_vendor(self, db: AsyncSession, vendor_id: int) -> Optional[Vendor]:
        result = await db.execute(
            select(Vendor).filter(Vendor.id == vendor_id)
        )
        return result.scalars().first()

    async def get_vendor_by_name(self, db: AsyncSession, name: str, owner_id: int) -> Optional[Vendor]:
        result = await db.execute(
            select(Vendor).filter(Vendor.name == name, Vendor.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_vendors(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Vendor]:
        result = await db.execute(
            select(Vendor).filter(Vendor.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_vendor(self, db: AsyncSession, vendor_in: VendorCreate, owner_id: int) -> Vendor:
        db_vendor = Vendor(**vendor_in.dict(), owner_id=owner_id)
        db.add(db_vendor)
        try:
            await db.commit()
            await db.refresh(db_vendor)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the vendor: " + str(e))
        return db_vendor

    async def update_vendor(self, db: AsyncSession, db_vendor: Vendor, vendor_in: VendorUpdate) -> Vendor:
        update_data = vendor_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_vendor, key, value)
        try:
            await db.commit()
            await db.refresh(db_vendor)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the vendor: " + str(e))
        return db_vendor

    async def delete_vendor(self, db: AsyncSession, vendor_id: int):
        db_vendor = await self.get_vendor(db, vendor_id)
        if db_vendor:
            await db.delete(db_vendor)
            await db.commit()
        return db_vendor

# Initialize the CRUD object
crud_vendor = CRUDVendor()
