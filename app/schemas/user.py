# app/schemas/user.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.property_summary import PropertySummary

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    profile_pic: Optional[str] = None

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = False  # Allow setting is_admin during user creation (optional)

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    profile_pic: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None  # Allow updating is_admin (admin only)

class UserInDBBase(UserBase):
    id: int
    is_admin: bool  # Include is_admin in the base DB schema

    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    properties: Optional[List[PropertySummary]] = []

    model_config = ConfigDict(from_attributes=True)

class UserMe(UserInDBBase):
    """Schema for /users/me endpoint without properties."""
    model_config = ConfigDict(from_attributes=True)