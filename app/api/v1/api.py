"""Main API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import watchlist, auth, stripe_webhook

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(stripe_webhook.router, prefix="/stripe", tags=["stripe"]) 