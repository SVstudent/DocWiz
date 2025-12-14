"""Patient profile routes."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1 import Client

from app.api.dependencies import get_current_active_user
from app.db.base import get_db
from app.db.models import User
from app.schemas.profile import (
    PatientProfileCreate,
    PatientProfileResponse,
    PatientProfileUpdate,
    ProfileVersionHistoryResponse,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_profile_service(db: Client = Depends(get_db)) -> ProfileService:
    """Dependency for getting profile service."""
    return ProfileService(db)


@router.get("/me", response_model=PatientProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> PatientProfileResponse:
    """Get current user's profile."""
    # Get profile by user_id
    profile = await profile_service.get_profile_by_user_id(current_user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Decrypt sensitive fields for response
    profile_dict = profile_service.decrypt_profile_for_response(profile)
    
    return PatientProfileResponse(**profile_dict)


@router.post("", response_model=PatientProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: PatientProfileCreate,
    current_user: User = Depends(get_current_active_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> PatientProfileResponse:
    """Create a new patient profile."""
    # Validate profile data
    validation_result = await profile_service.validate_profile(profile_data)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Profile validation failed",
                "missing_fields": validation_result.missing_fields,
                "invalid_fields": validation_result.invalid_fields
            }
        )
    
    # Create profile
    profile = await profile_service.create_profile(current_user.id, profile_data)
    
    # Decrypt sensitive fields for response
    profile_dict = profile_service.decrypt_profile_for_response(profile)
    
    return PatientProfileResponse(**profile_dict)


@router.get("/{profile_id}", response_model=PatientProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> PatientProfileResponse:
    """Get patient profile by ID."""
    profile = await profile_service.get_profile(profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Check if user owns this profile
    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    # Decrypt sensitive fields for response
    profile_dict = profile_service.decrypt_profile_for_response(profile)
    
    return PatientProfileResponse(**profile_dict)


@router.put("/{profile_id}", response_model=PatientProfileResponse)
async def update_profile(
    profile_id: str,
    updates: PatientProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> PatientProfileResponse:
    """Update patient profile."""
    # Check if profile exists and user owns it
    existing_profile = await profile_service.get_profile(profile_id)
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    if existing_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Update profile
    updated_profile = await profile_service.update_profile(profile_id, updates)
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Decrypt sensitive fields for response
    profile_dict = profile_service.decrypt_profile_for_response(updated_profile)
    
    return PatientProfileResponse(**profile_dict)


@router.get("/{profile_id}/history", response_model=List[ProfileVersionHistoryResponse])
async def get_profile_history(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> List[ProfileVersionHistoryResponse]:
    """Get profile version history."""
    # Check if profile exists and user owns it
    profile = await profile_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile history"
        )
    
    # Get history
    history = await profile_service.get_profile_history(profile_id)
    
    return [ProfileVersionHistoryResponse(**h.model_dump()) for h in history]


@router.get("/{profile_id}/visualizations")
async def get_profile_visualizations(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db),
) -> List[dict]:
    """Get all visualizations for a specific profile."""
    from app.db.base import Collections
    
    # Query visualizations for this profile/patient
    # Don't require profile to exist - just return visualizations if any
    visualizations = []
    try:
        from google.cloud.firestore_v1.base_query import FieldFilter
        
        # Query by patient_id (which is the profile_id in visualizations)
        viz_docs = db.collection(Collections.VISUALIZATIONS).where(
            filter=FieldFilter("patient_id", "==", profile_id)
        ).stream()
        
        for doc in viz_docs:
            viz_data = doc.to_dict()
            viz_data["id"] = doc.id
            visualizations.append(viz_data)
    except Exception as e:
        # Return empty list if query fails
        pass
    
    return visualizations
