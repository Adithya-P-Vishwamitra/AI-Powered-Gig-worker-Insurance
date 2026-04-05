import os
import httpx
import logging
from typing import Dict, List
import googlemaps
from twilio.rest import Client as TwilioClient
from newsapi import NewsApiClient

logger = logging.getLogger(__name__)

class ExternalAPIService:
    def __init__(self):
        # 1. OpenWeather
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        
        # 2. Twilio
        self.twilio_sid = os.getenv("TWILIO_SID", "")
        self.twilio_token = os.getenv("TWILIO_TOKEN", "")
        self.twilio_from = os.getenv("TWILIO_FROM_NUMBER", "+1234567890")
        self.twilio_client = TwilioClient(self.twilio_sid, self.twilio_token) if self.twilio_sid and self.twilio_token else None
        
        # 3. Razorpay (Mocked)
        self.rzp_client = None # Explicitly mocked below
        
        # 4. Google Maps
        self.gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.gmaps_client = googlemaps.Client(key=self.gmaps_key) if self.gmaps_key else None
        
        # 5. NewsAPI
        self.news_key = os.getenv("NEWS_API_KEY", "")
        self.news_client = NewsApiClient(api_key=self.news_key) if self.news_key else None

    async def get_weather(self, lat: float, lon: float) -> Dict:
        """Fetch real-time weather using OpenWeatherMap"""
        if not self.weather_api_key:
            return {"rain_mm": 55, "aqi": 8, "description": "heavy rain (MOCK)"}

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                rain = data.get("rain", {}).get("1h", 0)
                aqi = 5 # OpenWeather AQI is a separate endpoint (air_pollution), so mock it slightly or add a second call
                return {"rain_mm": rain, "aqi": aqi, "description": data.get("weather", [{}])[0].get("description", "clear")}
        except Exception as e:
            logger.error(f"Weather API failed: {e}")
            return {"rain_mm": 0, "aqi": 0, "description": "unknown"}

    def get_traffic_congestion(self, origin: str, destination: str) -> str:
        """Fetch traffic condition using Google Maps Directions API"""
        if not self.gmaps_client:
            return "Heavy (MOCK)"
        try:
            directions = self.gmaps_client.directions(
                origin, 
                destination, 
                departure_time="now", 
                traffic_model="best_guess"
            )
            if directions:
                leg = directions[0]['legs'][0]
                duration_in_traffic = leg.get('duration_in_traffic', {}).get('value', 0)
                duration = leg.get('duration', {}).get('value', 1) # avoid division by 0
                ratio = duration_in_traffic / duration
                if ratio > 1.5: return "Severe"
                elif ratio > 1.2: return "Heavy"
                else: return "Normal"
            return "Unknown"
        except Exception as e:
            logger.error(f"GMaps API failed: {e}")
            return "Unknown"

    def check_local_news_disruption(self, location: str) -> List[str]:
        """Fetch local news about floods or accidents from NewsAPI"""
        if not self.news_client:
            return ["Heavy rains disrupt daily life in zone (MOCK)"]
        try:
            headlines = self.news_client.get_top_headlines(
                q='flood OR rain OR accident OR traffic',
                language='en',
                country='in'
            )
            return [article['title'] for article in headlines.get('articles', [])[:3]]
        except Exception as e:
            logger.error(f"NewsAPI failed: {e}")
            return []

    def trigger_payout(self, amount: float, account_id: str) -> bool:
        """Process test payout using a mocked Razorpay gateway"""
        logger.info(f"MOCK PAYOUT API: Simulating transfer of INR {amount} to account {account_id} via Razorpay Mock")
        return True

    def send_sms(self, phone: str, message: str) -> bool:
        """Send Twilio SMS notification"""
        if not self.twilio_client:
            logger.info(f"MOCK SMS to {phone}: {message}")
            return True
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from,
                to=phone
            )
            logger.info(f"TWILIO SMS SUCCESS to {phone}")
            return True
        except Exception as e:
            logger.error(f"Twilio SMS Failed: {e}")
            return False

api_service = ExternalAPIService()
