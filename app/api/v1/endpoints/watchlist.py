"""Watchlist endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistCreate, WatchlistRead, WatchlistUpdate
from app.services.watchlist_service import WatchlistService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=WatchlistRead)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new watchlist."""
    watchlist_service = WatchlistService(db)
    
    # Check user plan limits
    user_watchlists = await watchlist_service.get_by_user_id(current_user.id)
    if current_user.plan == "FREE" and len(user_watchlists) >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Free plan limited to 3 watchlists. Upgrade to PRO for unlimited."
        )
    
    watchlist = await watchlist_service.create(user_id=current_user.id, watchlist_data=watchlist_data)
    return watchlist


@router.get("/", response_model=List[WatchlistRead])
async def get_watchlists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all watchlists for the current user."""
    watchlist_service = WatchlistService(db)
    watchlists = await watchlist_service.get_by_user_id(current_user.id)
    return watchlists


@router.get("/{watchlist_id}", response_model=WatchlistRead)
async def get_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get a specific watchlist."""
    watchlist_service = WatchlistService(db)
    watchlist = await watchlist_service.get_by_id(watchlist_id)
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )
    
    if watchlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this watchlist"
        )
    
    return watchlist


@router.put("/{watchlist_id}", response_model=WatchlistRead)
async def update_watchlist(
    watchlist_id: int,
    update_data: WatchlistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update a watchlist."""
    watchlist_service = WatchlistService(db)
    watchlist = await watchlist_service.get_by_id(watchlist_id)
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )
    
    if watchlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this watchlist"
        )
    
    updated_watchlist = await watchlist_service.update(watchlist_id, update_data)
    return updated_watchlist


@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a watchlist."""
    watchlist_service = WatchlistService(db)
    watchlist = await watchlist_service.get_by_id(watchlist_id)
    
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )
    
    if watchlist.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this watchlist"
        )
    
    await watchlist_service.delete(watchlist_id)
    return {"message": "Watchlist deleted successfully"} 