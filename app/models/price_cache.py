"""Price cache model."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, JSON, Column


class PriceCache(SQLModel, table=True):
    """Price cache model."""
    __tablename__ = "price_cache"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="watchlist.id")
    offer_id: str = Field(index=True)  # Amadeus offer ID
    price: float = Field(gt=0)
    currency: str = Field(default="BRL")
    airlines: str  # Comma-separated airline codes
    stops: int = Field(default=0, ge=0)
    duration: str  # Total duration string (e.g., "10h30m")
    offer_data: Dict[str, Any] = Field(sa_column=Column(JSON))  # Full offer JSON
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    watchlist: "Watchlist" = Relationship(back_populates="price_caches")


class PriceCacheCreate(SQLModel):
    """Price cache creation schema."""
    watchlist_id: int
    offer_id: str
    price: float
    currency: str = "BRL"
    airlines: str
    stops: int = 0
    duration: str
    offer_data: Dict[str, Any]
    expires_at: Optional[datetime] = None


class PriceCacheRead(SQLModel):
    """Price cache read schema."""
    id: int
    watchlist_id: int
    offer_id: str
    price: float
    currency: str
    airlines: str
    stops: int
    duration: str
    fetched_at: datetime
    expires_at: Optional[datetime] 