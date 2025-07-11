"""Alert model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class AlertStatus(str, Enum):
    """Alert status types."""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class Alert(SQLModel, table=True):
    """Alert model."""
    __tablename__ = "alerts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="watchlist.id")
    price_cache_id: int = Field(foreign_key="price_cache.id")
    price: float = Field(gt=0)
    currency: str = Field(default="BRL")
    channel: str  # EMAIL or TELEGRAM
    status: AlertStatus = Field(default=AlertStatus.PENDING)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = Field(default=None)
    
    # Relationships
    watchlist: "Watchlist" = Relationship(back_populates="alerts")


class AlertCreate(SQLModel):
    """Alert creation schema."""
    watchlist_id: int
    price_cache_id: int
    price: float
    currency: str = "BRL"
    channel: str


class AlertRead(SQLModel):
    """Alert read schema."""
    id: int
    watchlist_id: int
    price: float
    currency: str
    channel: str
    status: AlertStatus
    sent_at: Optional[datetime]
    created_at: datetime 