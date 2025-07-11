"""Notification service for sending alerts via email and Telegram."""

import httpx
from typing import Dict, Any
from app.core.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via email and Telegram."""
    
    def __init__(self):
        self.sendgrid_client = None
        if settings.SENDGRID_API_KEY:
            self.sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        
        self.telegram_token = settings.TELEGRAM_BOT_TOKEN
    
    async def send_email_alert(self, user_email: str, watchlist, flight_info: Dict[str, Any]) -> bool:
        """Send price alert via email."""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured, skipping email alert")
            return False
        
        try:
            # Format flight details
            price = flight_info["price"]
            currency = flight_info["currency"]
            airlines = flight_info["airlines"]
            duration = flight_info["duration"]
            stops = flight_info["stops"]
            
            # Create email content
            subject = f"🎯 Flight Alert: {watchlist.origin} → {watchlist.destination} for {currency} {price:.2f}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: white; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">✈️ Flight Hunter Alert</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">We found a flight matching your criteria!</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #28a745; margin-top: 0;">🎯 Price Target Hit!</h2>
                        
                        <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                            <div style="text-align: center;">
                                <div style="font-size: 18px; font-weight: bold; color: #333;">{watchlist.origin}</div>
                                <div style="color: #666; font-size: 14px;">Origin</div>
                            </div>
                            <div style="text-align: center; color: #007bff;">
                                <div style="font-size: 24px;">✈️</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 18px; font-weight: bold; color: #333;">{watchlist.destination}</div>
                                <div style="color: #666; font-size: 14px;">Destination</div>
                            </div>
                        </div>
                        
                        <div style="background: #e7f3ff; padding: 15px; border-radius: 6px; margin: 15px 0;">
                            <div style="font-size: 32px; font-weight: bold; color: #007bff; text-align: center;">
                                {currency} {price:.2f}
                            </div>
                            <div style="text-align: center; color: #666; font-size: 14px;">
                                Target: {currency} {watchlist.price_target:.2f}
                            </div>
                        </div>
                        
                        <div style="margin: 15px 0;">
                            <strong>Flight Details:</strong><br>
                            🏢 Airlines: {airlines}<br>
                            ⏱️ Duration: {duration}<br>
                            🔄 Stops: {stops}<br>
                            👥 Passengers: {watchlist.pax}<br>
                            📅 Date: {watchlist.date_from}
                        </div>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="https://www.google.com/flights?q={watchlist.origin}%20to%20{watchlist.destination}%20{watchlist.date_from}" 
                               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Book Now on Google Flights
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                        <p>This alert was sent by Flight Hunter. To manage your watchlists, visit our dashboard.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_content = f"""
Flight Hunter Alert - Price Target Hit!

Route: {watchlist.origin} → {watchlist.destination}
Price: {currency} {price:.2f} (Target: {currency} {watchlist.price_target:.2f})
Airlines: {airlines}
Duration: {duration}
Stops: {stops}
Passengers: {watchlist.pax}
Date: {watchlist.date_from}

Book now: https://www.google.com/flights?q={watchlist.origin}%20to%20{watchlist.destination}%20{watchlist.date_from}
            """
            
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=user_email,
                subject=subject,
                plain_text_content=plain_content,
                html_content=html_content
            )
            
            response = self.sendgrid_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email alert sent successfully to {user_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
            return False
    
    async def send_telegram_alert(self, chat_id: str, watchlist, flight_info: Dict[str, Any]) -> bool:
        """Send price alert via Telegram."""
        if not self.telegram_token:
            logger.warning("Telegram bot token not configured, skipping Telegram alert")
            return False
        
        try:
            price = flight_info["price"]
            currency = flight_info["currency"]
            airlines = flight_info["airlines"]
            duration = flight_info["duration"]
            stops = flight_info["stops"]
            
            # Create Telegram message
            message = f"""
🎯 *Flight Alert - Price Target Hit!*

✈️ *{watchlist.origin} → {watchlist.destination}*

💰 *Price:* {currency} {price:.2f}
🎯 *Your Target:* {currency} {watchlist.price_target:.2f}
🏢 *Airlines:* {airlines}
⏱️ *Duration:* {duration}
🔄 *Stops:* {stops}
👥 *Passengers:* {watchlist.pax}
📅 *Date:* {watchlist.date_from}

[Book on Google Flights](https://www.google.com/flights?q={watchlist.origin}%20to%20{watchlist.destination}%20{watchlist.date_from})
            """
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown",
                        "disable_web_page_preview": False
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Telegram alert sent successfully to chat {chat_id}")
                    return True
                else:
                    logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {str(e)}")
            return False
    
    async def send_welcome_email(self, user_email: str) -> bool:
        """Send welcome email to new users."""
        if not self.sendgrid_client:
            return False
        
        try:
            subject = "Welcome to Flight Hunter! 🚀"
            
            html_content = """
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; color: white; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">✈️ Welcome to Flight Hunter!</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Your intelligent flight price monitoring assistant</p>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                    <h2 style="color: #333; margin-top: 0;">🎯 Start Saving on Flights!</h2>
                    
                    <p>Thank you for joining Flight Hunter! You're now ready to:</p>
                    
                    <ul style="color: #666; line-height: 1.6;">
                        <li>📊 Create watchlists for your desired routes</li>
                        <li>🎯 Set price targets and get notified when they're hit</li>
                        <li>📧 Receive instant alerts via email or Telegram</li>
                        <li>💰 Save money on your next trip</li>
                    </ul>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="color: #007bff; margin-top: 0;">🆓 Free Plan Features:</h3>
                        <ul style="color: #666; margin: 0;">
                            <li>Up to 3 active watchlists</li>
                            <li>Email and Telegram alerts</li>
                            <li>24/7 price monitoring</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                            Create Your First Watchlist
                        </a>
                    </div>
                    
                    <div style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                        <p>Questions? Reply to this email or contact our support team.</p>
                        <p style="margin: 0;">Happy hunting! 🎯</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=user_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False 