import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core.database import db
from services.external import api_service
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Track recent events in local cache to avoid spamming claims every 5 minutes
cache = {
    "last_rain_claim_time": None,
    "last_traffic_claim_time": None,
    "last_pollution_claim_time": None,
    "last_news_claim_time": None
}

def can_trigger(event_key: str, cooldown_hours: int = 12) -> bool:
    """Ensure we don't trigger the same event multiple times in a single day for a zone."""
    last_time = cache.get(event_key)
    if not last_time:
        return True
    
    elapsed = (datetime.now() - last_time).total_seconds() / 3600
    return elapsed > cooldown_hours

def scan_and_trigger_disruptions():
    """Background task evaluating APIs to generate automated zero-touch claims."""
    logger.info("Executing periodic Disruption Trigger Scan (Caching APIs)")
    
    zone = "Bengaluru"
    
    # Run async function in synchronous scheduler block
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    weather = loop.run_until_complete(api_service.get_weather(12.9716, 77.5946)) # Bengaluru Coords
    loop.close()
    
    rain_mm = weather.get("rain_mm", 0)
    aqi = weather.get("aqi", 0)
    
    # Check Traffic
    traffic_status = api_service.get_traffic_congestion("12.9716,77.5946", "13.00,77.60")
    
    # Check Emergency News
    news = api_service.check_local_news_disruption(zone)
    
    # Evaluators
    triggered = False
    event_type = ""
    reason = ""
    payout_base = 0

    # 1. Rainfall Trigger (>20mm)
    if rain_mm > 20 and can_trigger("last_rain_claim_time"):
        event_type = "Heavy Rainfall"
        reason = f"Continuous heavy rain detected ({rain_mm}mm)."
        payout_base = 250
        cache["last_rain_claim_time"] = datetime.now()
        triggered = True

    # 2. Extreme AQI / Heat
    elif aqi > 300 and can_trigger("last_pollution_claim_time"):
        event_type = "Severe Air Quality"
        reason = f"AQI reached hazardous levels ({aqi})."
        payout_base = 150
        cache["last_pollution_claim_time"] = datetime.now()
        triggered = True

    # 3. Traffic Gridlock
    elif traffic_status == "Heavy" and can_trigger("last_traffic_claim_time"):
        event_type = "Gridlock"
        reason = "Severe unexpected traffic delays exceeding 150% baseline."
        payout_base = 200
        cache["last_traffic_claim_time"] = datetime.now()
        triggered = True

    # 4. News APIs (Protests/Floods)
    elif len(news) > 0 and can_trigger("last_news_claim_time"):
        event_type = "Local Disturbance"
        title = news[0] if isinstance(news[0], str) else news[0].get('title', 'Unknown')
        reason = f"Local alert detected: {title}"
        payout_base = 300
        cache["last_news_claim_time"] = datetime.now()
        triggered = True

    if triggered:
        logger.info(f"DISRUPTION TRIGGERED: {event_type} - Dispensing Claims for Zone: {zone}")
        # Log event globally
        db.add_disruption_event({
            "zone": zone,
            "type": event_type,
            "severity": "High",
            "timestamp": datetime.now().isoformat()
        })
        
        # Pull all active users in that zone and auto-dispense claims!
        affected_users = db.get_users_by_location(zone)
        for user in affected_users:
            u_id = user["id"]
            db.add_claim(u_id, {
                "event_type": event_type,
                "reason": reason,
                "payout_amount": payout_base,
                "timestamp": datetime.now().isoformat()
            })
            api_service.trigger_payout(payout_base, f"user_bank_{u_id}")
            logger.info(f"Zero-Touch Claim deposited for user {u_id}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 5 minutes
    scheduler.add_job(
        scan_and_trigger_disruptions,
        trigger=IntervalTrigger(minutes=5),
        id='disruption_scan_job',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Automated Disruption Scheduler background loop started successfully.")
