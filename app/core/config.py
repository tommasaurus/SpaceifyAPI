# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REGRID_API_KEY: str = Field(..., env="REGRID_API_KEY")
    GOOGLE_STREET_VIEW_API_KEY: str = Field(..., env="GOOGLE_STREET_VIEW_API_KEY")
    
    # OAuth client details for Google
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    # JWT configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    REFRESH_SECRET_KEY: str = Field(..., env="REFRESH_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()
