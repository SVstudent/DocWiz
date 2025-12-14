"""Authentication service."""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from google.cloud.firestore_v1 import Client
from google.cloud.firestore_v1.base_query import FieldFilter
from jose import JWTError, jwt

from app.config import settings
from app.db.base import Collections
from app.db.models import User


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Client, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    # Query Firestore for user by email
    users_ref = db.collection(Collections.USERS)
    query = users_ref.where(filter=FieldFilter("email", "==", email)).limit(1)
    docs = query.stream()
    
    user_doc = None
    for doc in docs:
        user_doc = doc
        break
    
    if not user_doc:
        return None
    
    user_data = user_doc.to_dict()
    user = User.from_dict(user_data)
    
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Client, email: str, password: str) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    
    # Save to Firestore
    user_dict = user.to_dict()
    db.collection(Collections.USERS).document(user.id).set(user_dict)
    
    return user


def get_user_by_email(db: Client, email: str) -> Optional[User]:
    """Get a user by email."""
    users_ref = db.collection(Collections.USERS)
    query = users_ref.where(filter=FieldFilter("email", "==", email)).limit(1)
    docs = query.stream()
    
    for doc in docs:
        user_data = doc.to_dict()
        return User.from_dict(user_data)
    
    return None


def get_user_by_id(db: Client, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    doc_ref = db.collection(Collections.USERS).document(user_id)
    doc = doc_ref.get()
    
    if doc.exists:
        user_data = doc.to_dict()
        return User.from_dict(user_data)
    
    return None
