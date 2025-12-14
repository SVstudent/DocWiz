"""Firebase/Firestore database configuration."""
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client

from app.config import settings

# Global Firestore client
_db_client: Optional[Client] = None


def initialize_firestore() -> Client:
    """Initialize Firebase Admin SDK and return Firestore client."""
    global _db_client
    
    if _db_client is not None:
        return _db_client
    
    # Check if using Firestore emulator for local development
    if settings.use_firestore_emulator and settings.firestore_emulator_host:
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host
        print(f"Using Firestore Emulator at {settings.firestore_emulator_host}")
    
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        if settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path):
            # Use service account credentials
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id,
            })
        else:
            # Use Application Default Credentials (for Cloud Run, GCE, etc.)
            firebase_admin.initialize_app(options={
                'projectId': settings.firebase_project_id,
            })
    
    # Get Firestore client
    _db_client = firestore.client()
    return _db_client


def get_db() -> Client:
    """Dependency for getting Firestore database client."""
    if _db_client is None:
        return initialize_firestore()
    return _db_client


# Collection names (constants for consistency)
class Collections:
    """Firestore collection names."""
    USERS = "users"
    PATIENT_PROFILES = "patient_profiles"
    PROFILE_VERSION_HISTORY = "profile_version_history"
    PROCEDURES = "procedures"
    IMAGES = "images"
    VISUALIZATIONS = "visualization_results"
    VISUALIZATION_RESULTS = "visualization_results"  # Alias for consistency
    COST_BREAKDOWNS = "cost_breakdowns"
    PREAUTH_FORMS = "preauth_forms"
    COMPARISONS = "comparisons"
    COMPARISON_SETS = "comparisons"  # Alias for consistency
    EXPORTS = "exports"
