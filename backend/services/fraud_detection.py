import math
from typing import Dict, Tuple

class FraudDetectionService:
    def __init__(self):
        # Coordinates for Bengaluru center (approx)
        self.BLR_LAT = 12.9716
        self.BLR_LON = 77.5946

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km using Haversine formula"""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def check_gps_anomaly(self, old_location: Tuple[float, float], new_location: Tuple[float, float], time_diff_minutes: float) -> bool:
        """Returns True if anomaly is detected (e.g. impossible speed)"""
        if time_diff_minutes <= 0:
            return True
        distance_km = self.calculate_distance(*old_location, *new_location)
        speed_kmh = distance_km / (time_diff_minutes / 60)
        
        # Delivery partners realistically max out around 60-80 km/h in city
        if speed_kmh > 100:
            return True
        return False

    def check_behavioral_anomaly(self, user_history: Dict) -> bool:
        """Returns True if user behavior is suspicious"""
        # Flag if they have too many claims in a short time
        if user_history.get("active_claims", 0) >= 3:
            return True
        return False

    def validate_claim(self, user_data: Dict, expected_location: str, actual_lat: float, actual_lon: float) -> Dict:
        """Perform all fraud checks"""
        result = {"is_valid": True, "reasons": []}
        
        # 1. Behavioral Check
        if self.check_behavioral_anomaly(user_data):
            result["is_valid"] = False
            result["reasons"].append("Excessive recent claims")

        # 2. Location validation. Mock check: are they roughly in Bangalore?
        dist_from_blr = self.calculate_distance(self.BLR_LAT, self.BLR_LON, actual_lat, actual_lon)
        if dist_from_blr > 50: # More than 50km from Bangalore center
            result["is_valid"] = False
            result["reasons"].append("Location outside active zone")

        return result

fraud_detector = FraudDetectionService()
