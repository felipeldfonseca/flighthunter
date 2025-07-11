"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.models.user import User, UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter()


# Dependency function for getting current authenticated user
async def get_current_user(db: AsyncSession = Depends(get_async_session)) -> User:
    """
    Get current authenticated user.
    This is a placeholder and will be replaced with real JWT authentication.
    For now, it fetches the first user from the database.
    """
    user_service = UserService(db)
    # In a real app, you'd decode a JWT token here.
    # For now, we'll just grab the first user to make dependency injection work.
    user = await user_service.get_by_id(1) 
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/register", response_model=UserRead)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    """Register a new user."""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await user_service.create(user_data)
    return user


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user 