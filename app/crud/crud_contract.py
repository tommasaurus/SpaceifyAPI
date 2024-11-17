# app/crud/crud_contract.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.contract import Contract
from app.models.property import Property
from app.schemas.contract import ContractCreate, ContractUpdate

class CRUDContract:
    async def get_contract(self, db: AsyncSession, contract_id: int, owner_id: int) -> Optional[Contract]:
        result = await db.execute(
            select(Contract)
            .options(
                selectinload(Contract.property),
                selectinload(Contract.vendor),
                selectinload(Contract.document)  
            )
            .join(Property)
            .filter(Contract.id == contract_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_contracts(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Contract]:
        result = await db.execute(
            select(Contract)
            .options(
                selectinload(Contract.property),
                selectinload(Contract.vendor),
                selectinload(Contract.document)  
            )
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_contract(self, db: AsyncSession, contract_in: ContractCreate, owner_id: int) -> Contract:
        # Verify that the property exists and belongs to the owner
        result = await db.execute(
            select(Property).filter(Property.id == contract_in.property_id, Property.owner_id == owner_id)
        )
        property = result.scalars().first()
        if not property:
            raise ValueError("Property not found or you do not have permission to access this property.")

        db_contract = Contract(**contract_in.dict())
        db.add(db_contract)
        try:
            await db.commit()
            await db.refresh(db_contract)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the contract: " + str(e))
        return db_contract

    async def update_contract(self, db: AsyncSession, db_contract: Contract, contract_in: ContractUpdate) -> Contract:
        update_data = contract_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contract, key, value)
        try:
            await db.commit()
            await db.refresh(db_contract)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the contract: " + str(e))
        return db_contract

    async def delete_contract(self, db: AsyncSession, contract_id: int, owner_id: int) -> Optional[Contract]:
        db_contract = await self.get_contract(db, contract_id, owner_id)
        if db_contract:
            await db.delete(db_contract)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the contract: " + str(e))
        return db_contract

# Initialize the CRUD object
crud_contract = CRUDContract()
