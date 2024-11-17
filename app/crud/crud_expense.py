# app/crud/crud_expense.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.expense import Expense
from app.models.property import Property
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

class CRUDExpense:
    async def get_expense(self, db: AsyncSession, expense_id: int, owner_id: int) -> Optional[Expense]:
        result = await db.execute(
            select(Expense)
            .options(
                selectinload(Expense.property),
                selectinload(Expense.vendor)
            )
            .join(Property)
            .filter(Expense.id == expense_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_expenses(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Expense]:
        result = await db.execute(
            select(Expense)
            .options(
                selectinload(Expense.property),
                selectinload(Expense.vendor)
            )
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_expenses_by_property(
        self,
        db: AsyncSession,
        property_id: int,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expense]:
        result = await db.execute(
            select(Expense)
            .options(
                selectinload(Expense.property),
                selectinload(Expense.vendor)
            )
            .join(Property, Expense.property_id == Property.id)
            .filter(Property.id == property_id)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_expense(self, db: AsyncSession, expense_in: ExpenseCreate, owner_id: int) -> Expense:
        # Verify that the property exists and belongs to the owner
        result = await db.execute(
            select(Property)
            .filter(Property.id == expense_in.property_id, Property.owner_id == owner_id)
        )
        property = result.scalars().first()
        if not property:
            raise ValueError("Property not found or you do not have permission to access this property.")

        db_expense = Expense(**expense_in.dict())
        db.add(db_expense)
        try:
            await db.commit()
            await db.refresh(db_expense, attribute_names=["property", "vendor"])  # Eagerly load relationships
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the expense: " + str(e))
        return db_expense

    async def update_expense(self, db: AsyncSession, db_expense: Expense, expense_in: ExpenseUpdate) -> Expense:
        update_data = expense_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_expense, key, value)
        try:
            await db.commit()
            await db.refresh(db_expense, attribute_names=["property", "vendor"])  # Eagerly load relationships
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the expense: " + str(e))
        return db_expense

    async def delete_expense(self, db: AsyncSession, expense_id: int, owner_id: int) -> Optional[Expense]:
        db_expense = await self.get_expense(db, expense_id, owner_id)
        if db_expense:
            await db.delete(db_expense)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the expense: " + str(e))
        return db_expense

# Initialize the CRUD object
crud_expense = CRUDExpense()
