"""Application configuration."""

import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "Flight Hunter"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "local"
    DEBUG: bool = True
    
    # Database - SQLite for local, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./flight_hunter.db"
    
    # Google Cloud SQL settings
    GOOGLE_CLOUD_PROJECT: str = ""
    CLOUD_SQL_INSTANCE_NAME: str = ""
    CLOUD_SQL_DATABASE_NAME: str = "flight_hunter"
    CLOUD_SQL_USER: str = ""
    CLOUD_SQL_PASSWORD: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # External APIs
    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"
    
    DUFFEL_TOKEN: str = ""
    DUFFEL_BASE_URL: str = "https://api.duffel.com"
    
    # Notifications
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "alerts@flighthunter.app"
    
    TELEGRAM_BOT_TOKEN: str = ""
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_FREE: str = ""
    STRIPE_PRICE_PRO: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


settings = Settings() 