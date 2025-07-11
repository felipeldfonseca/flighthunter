"""User service for user management."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.user import User, UserCreate, UserUpdate


class UserService:
    """User service class."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_data.dict())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.db.get(User, user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalars().first()
    
    async def get_by_stripe_customer_id(self, stripe_customer_id: str) -> Optional[User]:
        """Get user by Stripe customer ID."""
        statement = select(User).where(User.stripe_customer_id == stripe_customer_id)
        result = await self.db.execute(statement)
        return result.scalars().first()
    
    async def update(self, user_id: int, update_data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True 