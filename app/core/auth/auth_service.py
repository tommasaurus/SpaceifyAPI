# app/core/auth/auth_service.py

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from .utils import verify_password, get_password_hash
from .jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import List, Optional
from jose import JWTError

# Signup service
async def signup_user(db: AsyncSession, email: str, password: str, name: str):
    # Normalize the email
    normalized_email = email.strip().lower()

    # Check if the email already exists
    stmt = select(User).filter(User.email == normalized_email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user:
        if user.hashed_password is None:
            # The email is registered via OAuth
            raise HTTPException(
                status_code=400,
                detail="Email is associated with a social account. Please log in using that method."
            )
        else:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the user's password and create a new user
    hashed_password = get_password_hash(password)
    new_user = User(name=name, email=normalized_email, hashed_password=hashed_password)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"msg": "User created successfully"}

# Login service
async def login_user(db: AsyncSession, email: str, password: str):
    # Normalize the email
    normalized_email = email.strip().lower()

    # Check if the user exists in the database
    stmt = select(User).filter(User.email == normalized_email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if user.hashed_password is None:
        # The account is registered via OAuth
        raise HTTPException(
            status_code=400,
            detail="This account is registered via social login. Please log in using that method."
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Create both access and refresh tokens
    access_token = create_access_token(data={"sub": normalized_email})
    refresh_token = create_refresh_token(data={"sub": normalized_email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Service to refresh access token
async def refresh_access_token(refresh_token: str, db: AsyncSession):
    try:
        email = decode_refresh_token(refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Verify if the user still exists
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Create a new access token
    new_access_token = create_access_token(data={"sub": email})
    return {"access_token": new_access_token, "token_type": "bearer"}

# Get a user by ID
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    stmt = select(User).filter(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user

# Get all users with pagination
async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users

# Create a new user
async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    # Normalize the email
    normalized_email = user_in.email.strip().lower()

    # Check if the email already exists
    stmt = select(User).filter(User.email == normalized_email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the user's password
    hashed_password = get_password_hash(user_in.password)

    # Create a new user instance
    new_user = User(
        email=normalized_email,
        hashed_password=hashed_password,
        name=user_in.name,
        is_admin=user_in.is_admin or False  # Default to False if not provided
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return new_user

# Update an existing user
async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.dict(exclude_unset=True)
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        await db.commit()
        await db.refresh(db_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return db_user

# Delete a user by ID
async def delete_user(db: AsyncSession, user_id: int) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    await db.delete(user)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return user
