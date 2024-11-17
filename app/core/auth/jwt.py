# app/core/auth/jwt.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings

# Function to create a JWT access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Function to create a JWT refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Function to decode and verify an access token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError("Invalid token: subject missing")
        return email
    except JWTError as e:
        raise JWTError(f"Token validation error: {str(e)}")

# Function to decode and verify a refresh token
def decode_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError("Invalid refresh token: subject missing")
        return email
    except JWTError as e:
        raise JWTError(f"Refresh token validation error: {str(e)}")
