"""Stripe service for subscription management."""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from app.models.user import UserUpdate, PlanType
import logging

logger = logging.getLogger(__name__)


class StripeService:
    """Stripe service class."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    async def handle_subscription_created(self, subscription: Dict[str, Any]):
        """Handle subscription created event."""
        customer_id = subscription["customer"]
        user = await self.user_service.get_by_stripe_customer_id(customer_id)
        
        if user:
            # Update user to PRO plan
            await self.user_service.update(
                user.id,
                UserUpdate(plan=PlanType.PRO)
            )
            logger.info(f"User {user.email} upgraded to PRO plan")
        else:
            logger.warning(f"User not found for Stripe customer {customer_id}")
    
    async def handle_subscription_updated(self, subscription: Dict[str, Any]):
        """Handle subscription updated event."""
        customer_id = subscription["customer"]
        status = subscription["status"]
        
        user = await self.user_service.get_by_stripe_customer_id(customer_id)
        if not user:
            logger.warning(f"User not found for Stripe customer {customer_id}")
            return
        
        if status == "active":
            # Ensure user is on PRO plan
            if user.plan != PlanType.PRO:
                await self.user_service.update(
                    user.id,
                    UserUpdate(plan=PlanType.PRO)
                )
                logger.info(f"User {user.email} subscription reactivated")
        elif status in ["canceled", "unpaid", "past_due"]:
            # Downgrade to FREE plan
            await self.user_service.update(
                user.id,
                UserUpdate(plan=PlanType.FREE)
            )
            logger.info(f"User {user.email} downgraded to FREE plan due to status: {status}")
    
    async def handle_subscription_deleted(self, subscription: Dict[str, Any]):
        """Handle subscription deleted event."""
        customer_id = subscription["customer"]
        user = await self.user_service.get_by_stripe_customer_id(customer_id)
        
        if user:
            # Downgrade to FREE plan
            await self.user_service.update(
                user.id,
                UserUpdate(plan=PlanType.FREE)
            )
            logger.info(f"User {user.email} downgraded to FREE plan (subscription deleted)")
        else:
            logger.warning(f"User not found for Stripe customer {customer_id}")
    
    async def handle_payment_succeeded(self, invoice: Dict[str, Any]):
        """Handle successful payment."""
        customer_id = invoice["customer"]
        user = await self.user_service.get_by_stripe_customer_id(customer_id)
        
        if user:
            logger.info(f"Payment succeeded for user {user.email}")
        else:
            logger.warning(f"User not found for Stripe customer {customer_id}")
    
    async def handle_payment_failed(self, invoice: Dict[str, Any]):
        """Handle failed payment."""
        customer_id = invoice["customer"]
        user = await self.user_service.get_by_stripe_customer_id(customer_id)
        
        if user:
            logger.warning(f"Payment failed for user {user.email}")
            # Note: We don't immediately downgrade on payment failure
            # Stripe will handle retries and subscription status updates
        else:
            logger.warning(f"User not found for Stripe customer {customer_id}") 