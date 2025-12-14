"""Cost estimation routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1 import Client

from app.api.dependencies import get_current_active_user
from app.db.base import get_db
from app.db.models import User
from app.schemas.cost import (
    CostBreakdownCreate,
    CostBreakdownResponse,
    CostInfographicRequest,
)
from app.services.cost_estimation_service import CostEstimationService
from app.services.profile_service import ProfileService
from app.services.freepik_client import FreepikClient
from app.config import settings

router = APIRouter(prefix="/costs", tags=["costs"])


@router.post("/estimate", response_model=CostBreakdownResponse, status_code=status.HTTP_201_CREATED)
async def estimate_cost(
    request: CostBreakdownCreate,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db),
) -> CostBreakdownResponse:
    """Calculate cost estimate for a procedure.
    
    Args:
        request: Cost breakdown creation request
        current_user: Authenticated user
        db: Firestore client
    
    Returns:
        Complete cost breakdown with insurance calculations and payment plans
    
    Raises:
        HTTPException: If patient profile or procedure not found
    """
    # Get patient profile
    profile_service = ProfileService(db)
    patient_profile = await profile_service.get_profile(request.patient_id)
    
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile not found: {request.patient_id}"
        )
    
    # Verify user owns this profile
    if patient_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    # Calculate cost breakdown
    cost_service = CostEstimationService(db)
    
    try:
        breakdown = await cost_service.calculate_cost_breakdown(
            procedure_id=request.procedure_id,
            patient_profile=patient_profile,
        )
        return breakdown
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{cost_id}", response_model=CostBreakdownResponse)
async def get_cost_breakdown(
    cost_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db),
) -> CostBreakdownResponse:
    """Get cost breakdown by ID.
    
    Args:
        cost_id: Cost breakdown identifier
        current_user: Authenticated user
        db: Firestore client
    
    Returns:
        Cost breakdown details
    
    Raises:
        HTTPException: If cost breakdown not found or unauthorized
    """
    cost_service = CostEstimationService(db)
    breakdown = await cost_service.get_cost_breakdown(cost_id)
    
    if not breakdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cost breakdown not found: {cost_id}"
        )
    
    # Verify user owns the associated profile
    profile_service = ProfileService(db)
    patient_profile = await profile_service.get_profile(breakdown.patient_id)
    
    if not patient_profile or patient_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this cost breakdown"
        )
    
    return breakdown


@router.get("/{cost_id}/infographic")
async def get_cost_infographic(
    cost_id: str,
    format: str = "png",
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db),
) -> dict:
    """Get visual cost breakdown infographic.
    
    Args:
        cost_id: Cost breakdown identifier
        format: Output format (png or jpeg)
        current_user: Authenticated user
        db: Firestore client
    
    Returns:
        Dict containing infographic URL and metadata
    
    Raises:
        HTTPException: If cost breakdown not found or unauthorized
    """
    # Validate format
    if format not in ["png", "jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'png' or 'jpeg'"
        )
    
    # Get cost breakdown
    cost_service = CostEstimationService(db)
    breakdown = await cost_service.get_cost_breakdown(cost_id)
    
    if not breakdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cost breakdown not found: {cost_id}"
        )
    
    # Verify user owns the associated profile
    profile_service = ProfileService(db)
    patient_profile = await profile_service.get_profile(breakdown.patient_id)
    
    if not patient_profile or patient_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this cost breakdown"
        )
    
    # Generate infographic using Freepik
    freepik_client = FreepikClient()
    
    try:
        cost_data = {
            "total_cost": float(breakdown.total_cost),
            "surgeon_fee": float(breakdown.surgeon_fee),
            "facility_fee": float(breakdown.facility_fee),
            "anesthesia_fee": float(breakdown.anesthesia_fee),
            "post_op_care": float(breakdown.post_op_care),
            "insurance_coverage": float(breakdown.insurance_coverage),
            "patient_responsibility": float(breakdown.patient_responsibility),
        }
        
        result = await freepik_client.generate_cost_infographic(
            cost_data=cost_data,
            format=format,
            style="professional"
        )
        
        return {
            "cost_id": cost_id,
            "infographic_url": result.get("image_url"),
            "format": format,
            "width": result.get("width"),
            "height": result.get("height"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate infographic: {str(e)}"
        )
