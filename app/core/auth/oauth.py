# app/core/auth/oauth.py

from authlib.integrations.starlette_client import OAuth
from jose import jwt
from app.core.config import settings

# Initialize OAuth configuration using Pydantic settings
oauth = OAuth()

# Register the OAuth2 provider (e.g., Google)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    refresh_token_url='https://oauth2.googleapis.com/token',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

