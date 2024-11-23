# app/crud/crud_income.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload 
from typing import List, Optional
from app.models.income import Income
from app.models.property import Property
from app.schemas.income import IncomeCreate, IncomeUpdate

class CRUDIncome:
    async def get_income(self, db: AsyncSession, income_id: int, owner_id: int) -> Optional[Income]:
        result = await db.execute(
            select(Income)
            .options(selectinload(Income.property))  
            .join(Property)
            .filter(Income.id == income_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_incomes(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Income]:
        result = await db.execute(
            select(Income)
            .options(selectinload(Income.property))  # Add this line
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_income(self, db: AsyncSession, income_in: IncomeCreate, owner_id: int) -> Income:
        # Verify that the property exists and belongs to the owner
        result = await db.execute(
            select(Property).filter(Property.id == income_in.property_id, Property.owner_id == owner_id)
        )
        property = result.scalars().first()
        if not property:
            raise ValueError("Property not found or you do not have permission to access this property.")

        db_income = Income(**income_in.dict())
        db.add(db_income)
        try:
            await db.commit()
            await db.refresh(db_income, attribute_names=["property"])  # Add property to attribute_names
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the income: " + str(e))
        return db_income

    async def update_income(self, db: AsyncSession, db_income: Income, income_in: IncomeUpdate) -> Income:
        update_data = income_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_income, key, value)
        try:
            await db.commit()
            await db.refresh(db_income, attribute_names=["property"])  # Add property to attribute_names
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the income: " + str(e))
        return db_income

    async def delete_income(self, db: AsyncSession, income_id: int, owner_id: int) -> bool:
        """Modified to return a boolean instead of the deleted object"""
        db_income = await self.get_income(db, income_id, owner_id)
        if db_income:
            await db.delete(db_income)
            try:
                await db.commit()
                return True
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the income: " + str(e))
        return False

# Initialize the CRUD object
crud_income = CRUDIncome()
