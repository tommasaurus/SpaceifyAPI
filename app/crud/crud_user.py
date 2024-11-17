# app/crud/crud_user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import Optional, List

class CRUDUser:
    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            name=user_in.name,
            is_admin=user_in.is_admin or False  # Ensure is_admin is set
        )
        db.add(db_user)
        try:
            await db.commit()
            await db.refresh(db_user)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while creating the user: " + str(e))
        return db_user

    async def update_user(self, db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
        update_data = user_in.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        for key, value in update_data.items():
            setattr(db_user, key, value)
        try:
            await db.commit()
            await db.refresh(db_user)
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("An error occurred while updating the user: " + str(e))
        return db_user

    async def delete_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        user = await self.get_user(db, user_id)
        if user:
            await db.delete(user)
            try:
                await db.commit()
            except IntegrityError as e:
                await db.rollback()
                raise ValueError("An error occurred while deleting the user: " + str(e))
            return user
        return None

# Initialize the CRUD object
crud_user = CRUDUser()
