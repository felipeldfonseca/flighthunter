"""Stripe webhook endpoints."""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
import json
from app.core.config import settings
from app.core.database import get_async_session
from app.services.stripe_service import StripeService

router = APIRouter()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_async_session)):
    """Handle Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    stripe_service = StripeService(db)
    
    if event["type"] == "customer.subscription.created":
        await stripe_service.handle_subscription_created(event["data"]["object"])
    elif event["type"] == "customer.subscription.updated":
        await stripe_service.handle_subscription_updated(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        await stripe_service.handle_subscription_deleted(event["data"]["object"])
    elif event["type"] == "invoice.payment_succeeded":
        await stripe_service.handle_payment_succeeded(event["data"]["object"])
    elif event["type"] == "invoice.payment_failed":
        await stripe_service.handle_payment_failed(event["data"]["object"])
    else:
        # Log unhandled event type
        print(f"Unhandled event type: {event['type']}")
    
    return {"status": "success"} 