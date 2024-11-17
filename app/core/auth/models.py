# app/core/auth/models.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

# User login request model
class UserLogin(BaseModel):
    email: str
    password: str

# User creation request model (for signup)
class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    is_admin: Optional[bool] = False  # Only settable by admin users

# Token response model (for login and OAuth)
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# Access token response model (for /refresh endpoint)
class AccessToken(BaseModel):
    access_token: str
    token_type: str

# Token data model (for token verification)
class TokenData(BaseModel):
    email: Optional[str] = None
