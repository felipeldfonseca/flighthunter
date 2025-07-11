"""Flight Hunter FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db
# Import all models to register them with SQLModel
from app.models import User, Watchlist, PriceCache, Alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Flight Hunter API",
    version="0.1.0",
    description="Flight price monitoring and alerts system",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The startup event is now handled by the lifespan context manager
# @app.on_event("startup")
# async def on_startup():
#     """Initialize database on startup."""
#     await init_db()
#     logger.info("Database tables created")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Flight Hunter API v0.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"} 