"""Database models (transitioning to Firestore).

Note: These models are being migrated to Firestore.
Simple Pydantic-style classes are used for now.
"""
import uuid
from datetime import datetime
from typing import Optional


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class User:
    """User model for authentication (Firestore-compatible)."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        email: str = "",
        hashed_password: str = "",
        is_active: bool = True
    ):
        self.id = id or generate_uuid()
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for Firestore."""
        return {
            "id": self.id,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create User from Firestore document."""
        user = cls()
        user.id = data.get("id")
        user.email = data.get("email", "")
        user.hashed_password = data.get("hashed_password", "")
        user.is_active = data.get("is_active", True)
        user.created_at = data.get("created_at", datetime.utcnow())
        user.updated_at = data.get("updated_at", datetime.utcnow())
        return user
