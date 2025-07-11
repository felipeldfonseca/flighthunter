"""Price monitoring service for background price checking."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from app.models.watchlist import Watchlist
from app.models.price_cache import PriceCache, PriceCacheCreate
from app.models.alert import Alert, AlertCreate, AlertStatus
from app.services.flight_service import FlightService
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class PriceMonitoringService:
    """Service for monitoring flight prices and triggering alerts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.flight_service = FlightService()
        self.notification_service = NotificationService()
    
    async def monitor_watchlist(self, watchlist: Watchlist) -> bool:
        """Monitor a single watchlist for price changes."""
        try:
            # Search for current flights
            offers = await self.flight_service.search_flights(
                origin=watchlist.origin,
                destination=watchlist.destination,
                departure_date=watchlist.date_from,
                adults=watchlist.pax,
                cabin_class=watchlist.cabin_class.value
            )
            
            if not offers:
                logger.warning(f"No flight offers found for watchlist {watchlist.id}")
                return False
            
            # Process each offer
            alerts_sent = 0
            for offer in offers:
                flight_info = self.flight_service.extract_flight_info(offer)
                
                # Check if price meets target
                if flight_info["price"] <= watchlist.price_target:
                    # Save to price cache
                    price_cache = self.save_price_cache(watchlist.id, flight_info)
                    
                    # Check if we already sent an alert for this offer recently
                    if not self.recent_alert_exists(watchlist.id, flight_info["offer_id"]):
                        # Send alert
                        alert = self.create_alert(watchlist, price_cache, flight_info)
                        if await self.send_alert(watchlist, alert, flight_info):
                            alerts_sent += 1
            
            logger.info(f"Processed watchlist {watchlist.id}: {len(offers)} offers, {alerts_sent} alerts sent")
            return True
            
        except Exception as e:
            logger.error(f"Error monitoring watchlist {watchlist.id}: {str(e)}")
            return False
    
    def save_price_cache(self, watchlist_id: int, flight_info: dict) -> PriceCache:
        """Save flight offer to price cache."""
        # Set expiration time (24 hours from now)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        price_cache_data = PriceCacheCreate(
            watchlist_id=watchlist_id,
            offer_id=flight_info["offer_id"],
            price=flight_info["price"],
            currency=flight_info["currency"],
            airlines=flight_info["airlines"],
            stops=flight_info["stops"],
            duration=flight_info["duration"],
            offer_data=flight_info["offer_data"],
            expires_at=expires_at
        )
        
        price_cache = PriceCache(**price_cache_data.dict())
        self.db.add(price_cache)
        self.db.commit()
        self.db.refresh(price_cache)
        
        return price_cache
    
    def recent_alert_exists(self, watchlist_id: int, offer_id: str, hours: int = 24) -> bool:
        """Check if an alert was sent for this offer recently."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        statement = select(Alert).join(PriceCache).where(
            Alert.watchlist_id == watchlist_id,
            PriceCache.offer_id == offer_id,
            Alert.created_at > cutoff_time,
            Alert.status == AlertStatus.SENT
        )
        
        existing_alert = self.db.exec(statement).first()
        return existing_alert is not None
    
    def create_alert(self, watchlist: Watchlist, price_cache: PriceCache, flight_info: dict) -> Alert:
        """Create an alert record."""
        alert_data = AlertCreate(
            watchlist_id=watchlist.id,
            price_cache_id=price_cache.id,
            price=flight_info["price"],
            currency=flight_info["currency"],
            channel=watchlist.channel.value
        )
        
        alert = Alert(**alert_data.dict())
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    async def send_alert(self, watchlist: Watchlist, alert: Alert, flight_info: dict) -> bool:
        """Send alert notification."""
        try:
            if watchlist.channel.value == "EMAIL":
                success = await self.notification_service.send_email_alert(
                    user_email=watchlist.user.email,
                    watchlist=watchlist,
                    flight_info=flight_info
                )
            elif watchlist.channel.value == "TELEGRAM":
                success = await self.notification_service.send_telegram_alert(
                    chat_id=watchlist.tg_chat_id or watchlist.user.tg_chat_id,
                    watchlist=watchlist,
                    flight_info=flight_info
                )
            else:
                logger.error(f"Unknown alert channel: {watchlist.channel}")
                success = False
            
            # Update alert status
            if success:
                alert.status = AlertStatus.SENT
                alert.sent_at = datetime.utcnow()
            else:
                alert.status = AlertStatus.FAILED
                alert.error_message = "Failed to send notification"
            
            self.db.add(alert)
            self.db.commit()
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending alert {alert.id}: {str(e)}")
            alert.status = AlertStatus.FAILED
            alert.error_message = str(e)
            self.db.add(alert)
            self.db.commit()
            return False
    
    def cleanup_expired_prices(self) -> int:
        """Clean up expired price cache entries."""
        cutoff_time = datetime.utcnow()
        
        # Delete expired entries
        statement = select(PriceCache).where(
            PriceCache.expires_at.isnot(None),
            PriceCache.expires_at < cutoff_time
        )
        
        expired_caches = self.db.exec(statement).all()
        count = len(expired_caches)
        
        for cache in expired_caches:
            self.db.delete(cache)
        
        self.db.commit()
        logger.info(f"Cleaned up {count} expired price cache entries")
        
        return count 