# app/api/endpoints/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas
from app.db.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.core.auth.auth_service import get_user_by_id, get_all_users, create_user, update_user, delete_user

router = APIRouter()

@router.get("/me", response_model=schemas.UserMe)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_current_user(
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated_user = await update_user(db=db, db_user=current_user, user_in=user_in)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Admin-only endpoints
@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)  # Only admin users can access this
):
    users = await get_all_users(db=db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    user = await get_user_by_id(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    user = await delete_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
