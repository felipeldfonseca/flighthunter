"""Flight service for Amadeus API integration."""

import httpx
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class FlightService:
    """Flight service for searching flights via Amadeus API."""
    
    def __init__(self):
        self.client_id = settings.AMADEUS_CLIENT_ID
        self.client_secret = settings.AMADEUS_CLIENT_SECRET
        self.base_url = settings.AMADEUS_BASE_URL
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """Get or refresh Amadeus access token."""
        if self.access_token and self.token_expires_at:
            if datetime.utcnow() < self.token_expires_at:
                return self.access_token
        
        # Request new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/security/oauth2/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                # Token expires in seconds, add buffer of 60 seconds
                expires_in = token_data.get("expires_in", 1799)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                return self.access_token
            else:
                logger.error(f"Failed to get Amadeus token: {response.status_code}")
                raise Exception("Failed to authenticate with Amadeus API")
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        adults: int = 1,
        cabin_class: str = "ECONOMY"
    ) -> List[Dict[str, Any]]:
        """Search for flights using Amadeus API."""
        if not self.client_id or not self.client_secret:
            logger.warning("Amadeus credentials not configured, returning mock data")
            return self._get_mock_flight_data(origin, destination, departure_date)
        
        token = await self.get_access_token()
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date.isoformat(),
            "adults": adults,
            "travelClass": cabin_class,
            "currencyCode": "BRL",
            "max": 50
        }
        
        if return_date:
            params["returnDate"] = return_date.isoformat()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/shopping/flight-offers",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Amadeus API error: {response.status_code} - {response.text}")
                # Return mock data as fallback
                return self._get_mock_flight_data(origin, destination, departure_date)
    
    def _get_mock_flight_data(self, origin: str, destination: str, departure_date: date) -> List[Dict[str, Any]]:
        """Generate mock flight data for testing."""
        import random
        import uuid
        
        mock_flights = []
        airlines = ["LA", "G3", "AD", "JJ"]
        
        for i in range(10):
            price = random.randint(200, 1500)
            stops = random.randint(0, 2)
            duration_hours = random.randint(2, 15)
            airline = random.choice(airlines)
            
            flight = {
                "id": str(uuid.uuid4()),
                "type": "flight-offer",
                "source": "GDS",
                "instantTicketingRequired": False,
                "nonHomogeneous": False,
                "oneWay": True,
                "lastTicketingDate": "2024-02-15",
                "numberOfBookableSeats": random.randint(1, 9),
                "price": {
                    "currency": "BRL",
                    "total": f"{price}.00",
                    "base": f"{price - 50}.00",
                    "fees": [{
                        "amount": "50.00",
                        "type": "SUPPLIER"
                    }],
                    "grandTotal": f"{price}.00"
                },
                "validatingAirlineCodes": [airline],
                "itineraries": [{
                    "duration": f"PT{duration_hours}H{random.randint(0, 59)}M",
                    "segments": [{
                        "departure": {
                            "iataCode": origin,
                            "at": f"{departure_date.isoformat()}T{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:00"
                        },
                        "arrival": {
                            "iataCode": destination,
                            "at": f"{departure_date.isoformat()}T{random.randint(8, 23):02d}:{random.randint(0, 59):02d}:00"
                        },
                        "carrierCode": airline,
                        "number": f"{random.randint(1000, 9999)}",
                        "aircraft": {"code": "320"},
                        "operating": {"carrierCode": airline},
                        "duration": f"PT{duration_hours}H{random.randint(0, 59)}M",
                        "id": f"{i+1}",
                        "numberOfStops": stops,
                        "blacklistedInEU": False
                    }]
                }]
            }
            mock_flights.append(flight)
        
        return mock_flights
    
    def extract_flight_info(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant flight information from Amadeus offer."""
        price = float(offer["price"]["total"])
        currency = offer["price"]["currency"]
        
        # Extract airline codes
        airlines = offer.get("validatingAirlineCodes", [])
        airlines_str = ",".join(airlines)
        
        # Calculate total stops and duration
        itinerary = offer["itineraries"][0]
        total_stops = sum(segment.get("numberOfStops", 0) for segment in itinerary["segments"])
        duration = itinerary["duration"]
        
        return {
            "offer_id": offer["id"],
            "price": price,
            "currency": currency,
            "airlines": airlines_str,
            "stops": total_stops,
            "duration": duration,
            "offer_data": offer
        } 