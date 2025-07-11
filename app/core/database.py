"""Database connection and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.core.config import settings

# Create async engine
async_engine = create_async_engine(
    str(settings.DATABASE_URL), 
    echo=settings.DEBUG,
    future=True
)

async def init_db():
    """Initialize database and create tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session() -> AsyncSession:
    """Get an async database session."""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session 