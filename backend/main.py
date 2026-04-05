from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from core.database import db
from ml.risk_model import risk_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Parametric Insurance API")

@app.on_event("startup")
def startup_event():
    from core.scheduler import start_scheduler
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserReg(BaseModel):
    id: Optional[str] = None
    name: str
    location: str
    base_income: float

class TriggerEvent(BaseModel):
    event_type: str # e.g. "heavy_rain"
    severity: float # 0 to 1
    location: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Gig Worker Insurance API Running"}

@app.post("/register")
async def register_user(user: UserReg):
    # Allow custom Firebase UID mapped dynamically
    user_id = db.add_user(user.dict())
    return {"user_id": user_id, "message": "User registered successfully"}

from services.external import api_service
from ml.risk_model import risk_model

@app.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    user = db.get_user(user_id)
    if not user:
        if user_id == "demo":
            # Auto bootstrap demo user for UI functionality
            db.add_user({"name": "Ravi (Demo)", "location": "Bengaluru", "base_income": 3000.0, "id": "demo"})
            user = db.get_user("demo")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Live data integration
    # Since location is a string like "Bengaluru", we map to coords roughly
    lat, lon = 12.9716, 77.5946
    weather_data = await api_service.get_weather(lat, lon)
    traffic_status = api_service.get_traffic_congestion("Kondapur", "Hitech City")
    news_alerts = api_service.check_local_news_disruption(user["location"])
    
    # Traffic dummy mapping for ML model
    traffic_score = 0.8 if traffic_status == "Heavy" else 0.5
    
    # Calculate Live Risk using ML
    rain_prob = 0.8 if weather_data["rain_mm"] > 5 else 0.1
    temperature = 28.0 # Default if undefined
    
    risk_prob = risk_model.predict_risk(
        rain_probability=rain_prob,
        temperature=temperature,
        historical_disruption=0.4,
        location_risk=0.6,
        seasonal_trend=0.5
    )
    
    daily_income = user.get("base_income", 3500) / 7.0
    weekly_premium = risk_model.calculate_weekly_premium(daily_income=daily_income, disruption_probability=risk_prob, days_lost=1)

    user["current_risk_score"] = risk_prob 
    user["weekly_premium"] = weekly_premium
    user["live_environment"] = {
        "rainfall": weather_data["rain_mm"],
        "aqi": weather_data["aqi"],
        "traffic": traffic_status,
        "description": weather_data["description"]
    }
    user["news_alerts"] = news_alerts
    return user

@app.get("/user/{user_id}/claims")
def get_user_claims(user_id: str):
    return db.get_claims_by_user(user_id)

async def process_disruption_event(event: TriggerEvent):
    """Background task to simulate finding affected users and triggering claims"""
    logger.info(f"Processing disruption event: {event.event_type} at {event.location}")
    await asyncio.sleep(2) # Simulate processing time
    
    # Save the event
    db.add_disruption_event(event.dict())
    
    # Find all users in the affected location
    affected_users = db.get_users_by_location(event.location)
    
    for user in affected_users:
        u_id = user["id"]
        # Check if severity is high enough to trigger a payout
        if event.severity > 0.6:
            # Expected loss calculation simplified
            payout = round(user["base_income"] * 0.5, 2)
            
            # Fraud check (mock)
            if user["active_claims"] > 2:
                status = "flagged_review"
            else:
                status = "approved_payout"
                
            claim_data = {
                "event_type": event.event_type,
                "payout_amount": payout,
                "status": status,
                "reason": "Auto-triggered via Environmental API Match"
            }
            db.add_claim(u_id, claim_data)
            logger.info(f"Claim automatically created for user {u_id}. Status: {status}")

@app.post("/simulate_event")
def simulate_external_disruption(event: TriggerEvent, background_tasks: BackgroundTasks):
    """Admin endpoint to mock receiving an external web-hook from Weather/News/Traffic APIs"""
    background_tasks.add_task(process_disruption_event, event)
    return {"message": "Event received and processing in background"}
