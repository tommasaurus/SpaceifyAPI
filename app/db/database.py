from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Set up the database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create the async engine and sessionmaker
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Base class for models
Base = declarative_base()

# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
