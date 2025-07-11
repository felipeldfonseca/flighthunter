"""Watchlist service for watchlist management."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.watchlist import Watchlist, WatchlistCreate, WatchlistUpdate


class WatchlistService:
    """Watchlist service class."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_id: int, watchlist_data: WatchlistCreate) -> Watchlist:
        """Create a new watchlist."""
        watchlist = Watchlist(**watchlist_data.dict(), user_id=user_id)
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        return watchlist
    
    async def get_by_id(self, watchlist_id: int) -> Optional[Watchlist]:
        """Get watchlist by ID."""
        return await self.db.get(Watchlist, watchlist_id)
    
    async def get_by_user_id(self, user_id: int) -> List[Watchlist]:
        """Get all watchlists for a user."""
        statement = select(Watchlist).where(Watchlist.user_id == user_id)
        result = await self.db.execute(statement)
        return result.scalars().all()
    
    async def get_active_watchlists(self) -> List[Watchlist]:
        """Get all active watchlists for monitoring."""
        statement = select(Watchlist).where(Watchlist.is_active == True)
        result = await self.db.execute(statement)
        return result.scalars().all()
    
    async def update(self, watchlist_id: int, update_data: WatchlistUpdate) -> Optional[Watchlist]:
        """Update watchlist."""
        watchlist = await self.get_by_id(watchlist_id)
        if not watchlist:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(watchlist, field, value)
        
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        return watchlist
    
    async def delete(self, watchlist_id: int) -> bool:
        """Delete watchlist."""
        watchlist = await self.get_by_id(watchlist_id)
        if not watchlist:
            return False
        
        await self.db.delete(watchlist)
        await self.db.commit()
        return True
    
    async def deactivate(self, watchlist_id: int) -> bool:
        """Deactivate watchlist instead of deleting."""
        watchlist = await self.get_by_id(watchlist_id)
        if not watchlist:
            return False
        
        watchlist.is_active = False
        self.db.add(watchlist)
        await self.db.commit()
        return True 