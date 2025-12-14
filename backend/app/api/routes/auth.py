"""Authentication routes."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1 import Client

from app.api.dependencies import get_current_active_user
from app.db.base import get_db
from app.db.models import User
from app.schemas.auth import LoginResponse, Token, UserLogin, UserRegister, UserResponse
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Client = Depends(get_db)) -> dict:
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = create_user(db, user_data.email, user_data.password)
    
    # Create access token for the new user
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.email.split('@')[0],  # Use email prefix as name for now
            "is_active": user.is_active
        }
    }


@router.post("/login")
async def login(user_data: UserLogin, db: Client = Depends(get_db)) -> dict:
    """Login user and return JWT token."""
    # Authenticate user
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.email.split('@')[0],  # Use email prefix as name for now
            "is_active": user.is_active
        }
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)) -> dict:
    """Refresh JWT token."""
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)) -> dict[str, str]:
    """Logout user (client should discard token)."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current user information."""
    return current_user
