"""Watchlist model."""

from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class CabinClass(str, Enum):
    """Cabin class types."""
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"


class AlertChannel(str, Enum):
    """Alert channel types."""
    EMAIL = "EMAIL"
    TELEGRAM = "TELEGRAM"


class Watchlist(SQLModel, table=True):
    """Watchlist model."""
    __tablename__ = "watchlist"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    origin: str = Field(index=True)  # IATA code
    destination: str = Field(index=True)  # IATA code
    date_from: date
    date_to: date
    flex_days: int = Field(default=0, ge=0, le=7)
    price_target: float = Field(gt=0)
    pax: int = Field(default=1, ge=1, le=9)
    cabin_class: CabinClass = Field(default=CabinClass.ECONOMY)
    channel: AlertChannel
    tg_chat_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Relationships
    user: "User" = Relationship(back_populates="watchlists")
    price_caches: List["PriceCache"] = Relationship(back_populates="watchlist")
    alerts: List["Alert"] = Relationship(back_populates="watchlist")


class WatchlistCreate(SQLModel):
    """Watchlist creation schema."""
    origin: str
    destination: str
    date_from: date
    date_to: date
    flex_days: int = Field(default=0, ge=0, le=7)
    price_target: float = Field(gt=0)
    pax: int = Field(default=1, ge=1, le=9)
    cabin_class: CabinClass = Field(default=CabinClass.ECONOMY)
    channel: AlertChannel
    tg_chat_id: Optional[str] = Field(default=None)


class WatchlistUpdate(SQLModel):
    """Watchlist update schema."""
    price_target: Optional[float] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


class WatchlistRead(SQLModel):
    """Watchlist read schema."""
    id: int
    origin: str
    destination: str
    date_from: date
    date_to: date
    flex_days: int
    price_target: float
    pax: int
    cabin_class: CabinClass
    channel: AlertChannel
    tg_chat_id: Optional[str]
    created_at: datetime
    is_active: bool 