import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)

class database:
    def __init__(self):
        try:
            # Initialize Firebase Admin with Service Account
            # Build the path to serviceAccountKey.json which lives in /backend/ folder
            # __file__ is in backend/core. So we go up 1 level.
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cred_path = os.path.join(backend_dir, "serviceAccountKey.json")
            
            if not firebase_admin._apps:
                if not os.path.exists(cred_path):
                    logger.warning(f"⚠️ serviceAccountKey.json not found at {cred_path}. Falling back to default credentials.")
                    firebase_admin.initialize_app()
                else:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
            
            self._db = firestore.client()
            logger.info(" Firebase Firestore connected successfully!")
        except Exception as e:
            logger.error(f" Firebase Init Failed: {e}")
            # Do not raise here to allow uvicorn reload to show error in logs without crashing
            self._db = None 

    def add_user(self, user_data: Dict) -> str:
        user_id = user_data.get('id', str(uuid.uuid4()))
        user_ref = self._db.collection("users").document(user_id)
        user_ref.set({**user_data, "id": user_id, "active_claims": 0}, merge=True)
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        user_ref = self._db.collection("users").document(user_id)
        doc = user_ref.get()
        return doc.to_dict() if doc.exists else None
        
    def add_claim(self, user_id: str, claim_data: Dict) -> str:
        claim_id = str(uuid.uuid4())
        claim_ref = self._db.collection("claims").document(claim_id)
        
        full_claim = {
            **claim_data,
            "id": claim_id,
            "user_id": user_id,
            "status": claim_data.get("status", "processing"),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        claim_ref.set(full_claim)
        
        # Increment active claims on user record
        user_ref = self._db.collection("users").document(user_id)
        user_ref.update({"active_claims": firestore.Increment(1)})
        
        return claim_id
        
    def get_claims_by_user(self, user_id: str) -> List[Dict]:
        query = self._db.collection("claims").where("user_id", "==", user_id).stream()
        return [doc.to_dict() for doc in query]

    def add_disruption_event(self, event_data: Dict) -> str:
        event_id = str(uuid.uuid4())
        event_ref = self._db.collection("events").document(event_id)
        event_ref.set({**event_data, "id": event_id, "created_at": firestore.SERVER_TIMESTAMP})
        return event_id

    def get_disruption_events(self) -> List[Dict]:
        query = self._db.collection("events").stream()
        return [doc.to_dict() for doc in query]

    def get_users_by_location(self, location: str) -> List[Dict]:
        query = self._db.collection("users").where("location", "==", location).stream()
        return [doc.to_dict() for doc in query]

# Global Instance
db = database()
