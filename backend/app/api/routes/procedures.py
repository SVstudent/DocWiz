"""Surgical procedure routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore_v1 import Client

from app.db.base import get_db
from app.schemas.procedure import (
    ProcedureResponse,
    ProcedureListResponse,
    CategoryListResponse,
    ProcedureDisplayResponse
)
from app.services.procedure_service import ProcedureService

router = APIRouter(prefix="/procedures", tags=["procedures"])


def get_procedure_service(db: Client = Depends(get_db)) -> ProcedureService:
    """Dependency to get procedure service instance."""
    return ProcedureService(db)


@router.get("", response_model=ProcedureListResponse)
async def list_procedures(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    service: ProcedureService = Depends(get_procedure_service)
):
    """List all available procedures.
    
    Optionally filter by category or search by name/description.
    
    Args:
        category: Optional category filter (e.g., 'facial', 'body', 'reconstructive')
        search: Optional search query for name or description
        service: Procedure service dependency
    
    Returns:
        List of procedures with total count
    """
    if category:
        procedures = await service.get_procedures_by_category(category)
    elif search:
        procedures = await service.search_procedures(search)
    else:
        procedures = await service.get_all_procedures()
    
    return ProcedureListResponse(
        procedures=[ProcedureResponse(**proc.model_dump()) for proc in procedures],
        total=len(procedures)
    )


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(
    service: ProcedureService = Depends(get_procedure_service)
):
    """List all procedure categories.
    
    Returns:
        List of unique category names with total count
    """
    categories = await service.get_all_categories()
    
    return CategoryListResponse(
        categories=categories,
        total=len(categories)
    )


@router.get("/{procedure_id}", response_model=ProcedureDisplayResponse)
async def get_procedure(
    procedure_id: str,
    service: ProcedureService = Depends(get_procedure_service)
):
    """Get procedure details by ID.
    
    Returns procedure information formatted for patient display,
    including description, recovery time, and risk factors as required
    by Requirements 1.2.
    
    Args:
        procedure_id: Unique procedure identifier
        service: Procedure service dependency
    
    Returns:
        Procedure details formatted for display
    
    Raises:
        HTTPException: 404 if procedure not found
    """
    procedure = await service.get_procedure_by_id(procedure_id)
    
    if not procedure:
        raise HTTPException(
            status_code=404,
            detail=f"Procedure with id '{procedure_id}' not found"
        )
    
    # Format for patient display per Requirements 1.2
    return ProcedureDisplayResponse(
        id=procedure.id,
        name=procedure.name,
        category=procedure.category,
        description=procedure.description,
        recovery_days=procedure.recovery_days,
        risk_level=procedure.risk_level,
        cost_range={
            "min": procedure.typical_cost_min,
            "max": procedure.typical_cost_max
        }
    )


@router.post("/initialize")
async def initialize_procedures(
    service: ProcedureService = Depends(get_procedure_service)
):
    """Initialize procedures in database from seed data.
    
    This endpoint should be called once during application setup
    to populate the procedures collection. It's idempotent - running
    it multiple times won't create duplicates.
    
    Returns:
        Number of procedures created
    """
    count = await service.initialize_procedures()
    
    return {
        "message": f"Successfully initialized {count} procedures",
        "count": count
    }
