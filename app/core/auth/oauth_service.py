# app/core/auth/oauth_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User
from .jwt import create_access_token, create_refresh_token
from app.core.auth.utils import get_password_hash
from jose import JWTError

async def authenticate_oauth_user(db: AsyncSession, token: dict):
    # Extract user info
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve user information from provider.")

    # Normalize the email
    email = user_info.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by the OAuth provider.")

    google_id = user_info.get("sub")
    name = user_info.get("name")
    profile_pic = user_info.get("picture")

    # Check if the user already exists
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user:
        if user.hashed_password:
            # The email is registered via email/password
            raise HTTPException(
                status_code=400,
                detail="This email is already registered. Please log in using your email and password."
            )
        else:
            # Update existing OAuth user info
            user.name = name
            user.profile_pic = profile_pic
            user.google_id = google_id
            await db.commit()
    else:
        # Create a new user for OAuth login
        new_user = User(
            google_id=google_id,
            email=email,
            name=name,
            profile_pic=profile_pic
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    # Generate both access and refresh tokens
    access_token = create_access_token(data={"sub": email})
    refresh_token = create_refresh_token(data={"sub": email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
