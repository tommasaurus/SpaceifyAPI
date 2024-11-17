# app/crud/crud_utility.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.utility import Utility
from app.models.property import Property
from app.schemas.utility import UtilityCreate, UtilityUpdate

class CRUDUtility:
    async def get_utility(self, db: AsyncSession, utility_id: int, owner_id: int) -> Optional[Utility]:
        result = await db.execute(
            select(Utility)            
            .join(Property)
            .filter(Utility.id == utility_id)
            .filter(Property.owner_id == owner_id)
        )
        return result.scalars().first()

    async def get_utilities(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Utility]:
        result = await db.execute(
            select(Utility)            
            .join(Property)
            .filter(Property.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    # async def create_utility(self, db: AsyncSession, utility_in: UtilityCreate, owner_id: int) -> Utility:
    #     # Verify that the property details exist and belong to the owner
    #     result = await db.execute(
    #         select(PropertyDetails)
    #         .join(Property)
    #         .filter(PropertyDetails.id == utility_in.property_details_id)
    #         .filter(Property.owner_id == owner_id)
    #     )
    #     property_details = result.scalars().first()
    #     if not property_details:
    #         raise ValueError("Property details not found or you do not have permission to access this property.")

    #     db_utility = Utility(**utility_in.dict())
    #     db.add(db_utility)
    #     try:
    #         await db.commit()
    #         await db.refresh(db_utility)
    #     except IntegrityError as e:
    #         await db.rollback()
    #         raise ValueError("An error occurred while creating the utility: " + str(e))
    #     return db_utility

    async def update_utility(self, db: AsyncSession, db_utility: Utility, utility_in: UtilityUpdate) -> Utility:
        update_data = utility_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_utility, key, value)
        try:
            await db.commit()
            await db.refresh(db_utility)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the utility: " + str(e))
        return db_utility

    async def delete_utility(self, db: AsyncSession, utility_id: int, owner_id: int) -> Optional[Utility]:
        db_utility = await self.get_utility(db, utility_id, owner_id)
        if db_utility:
            await db.delete(db_utility)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the utility: " + str(e))
        return db_utility

# Initialize the CRUD object
crud_utility = CRUDUtility()
