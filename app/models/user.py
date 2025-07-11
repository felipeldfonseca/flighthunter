"""User model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class PlanType(str, Enum):
    """User plan types."""
    FREE = "FREE"
    PRO = "PRO"


class User(SQLModel, table=True):
    """User model."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    plan: PlanType = Field(default=PlanType.FREE)
    stripe_customer_id: Optional[str] = Field(default=None)
    tg_chat_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    watchlists: list["Watchlist"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """User creation schema."""
    email: str
    tg_chat_id: Optional[str] = None


class UserUpdate(SQLModel):
    """User update schema."""
    plan: Optional[PlanType] = None
    stripe_customer_id: Optional[str] = None
    tg_chat_id: Optional[str] = None


class UserRead(SQLModel):
    """User read schema."""
    id: int
    email: str
    plan: PlanType
    created_at: datetime 