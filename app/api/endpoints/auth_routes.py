# app/api/endpoints/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.auth.auth_service import signup_user, login_user, refresh_access_token
from app.core.auth.oauth_service import authenticate_oauth_user
from app.core.auth.oauth import oauth
from app.core.config import settings
from app.core.auth.models import UserLogin, UserCreate, Token, AccessToken
from app.core.security import get_current_user
from app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Signup route
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
     return await signup_user(db, user.email, user.password, user.name)

# Login route
@router.post("/login", response_model=Token)
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    token_data = await login_user(db, user.email, user.password)
    # Set the refresh token as an HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=token_data["refresh_token"],
        httponly=True,
        secure=True,  # Use True in production with HTTPS
        samesite="Strict"  # Changed to Strict for better CSRF protection
    )
    # Return the access token in the response body
    return {"access_token": token_data["access_token"], "refresh_token": token_data["refresh_token"], "token_type": "bearer"}

# Logout route
@router.post("/logout")
async def logout(response: Response):
    # Clear the refresh token cookie
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}

# OAuth login route for Google
@router.get("/login/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    logger.info(f"Generated redirect_uri: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# OAuth callback route for Google login
@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        # Retrieve the token from the OAuth flow
        token = await oauth.google.authorize_access_token(request)

        # Authenticate the user or create a new one in the system
        token_data = await authenticate_oauth_user(db, token)

        # Redirect to dashboard on the frontend
        frontend_dashboard_url = "http://localhost:3000/dashboard"
        redirect_response = RedirectResponse(url=frontend_dashboard_url)

        # Set the refresh token as an HTTP-only cookie
        redirect_response.set_cookie(
            key="refresh_token",
            value=token_data["refresh_token"],
            httponly=True,
            secure=True,  # Use True in production with HTTPS
            samesite="Strict"  # Changed to Strict
        )

        # Optionally, you can have the frontend call /auth/refresh to get the access token

        return redirect_response

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error during Google OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

# Refresh Token Route
@router.post("/refresh", response_model=AccessToken)
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    new_token = await refresh_access_token(refresh_token=refresh_token, db=db)
    return new_token

# Check user authentication status
@router.get("/check")
async def check_user_auth(current_user: User = Depends(get_current_user)):
    """
    Route to check if the user is authenticated.
    """
    return {"status": "authenticated", "user": current_user.email}
