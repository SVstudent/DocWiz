"""Surgical visualization routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_active_user
from app.db.models import User
from app.schemas.visualization import (
    VisualizationRequest,
    VisualizationResult,
    SimilarCasesResponse,
    SimilarCase,
)
from app.schemas.comparison import (
    ComparisonRequest,
    ComparisonResult,
    ComparisonResponse,
)
from app.services.visualization_service import visualization_service, VisualizationError
from app.services.comparison_service import comparison_service, ComparisonError
from app.tasks.visualization_tasks import generate_visualization_task, generate_comparison_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visualizations", tags=["visualizations"])


@router.post("")
async def create_visualization(
    request: VisualizationRequest,
    async_processing: bool = Query(False, description="Process asynchronously using Celery"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a surgical visualization.
    
    This endpoint generates a photorealistic surgical preview using AI.
    Can be processed synchronously (default) or asynchronously (for long-running operations).
    
    If async_processing=true, returns a task_id that can be used to track progress.
    If async_processing=false, waits for completion and returns the result.
    
    Requirements: 1.3, 5.1, 9.5
    """
    try:
        logger.info(
            f"Creating visualization for user {current_user.id}, "
            f"image {request.image_id}, procedure {request.procedure_id}, "
            f"async={async_processing}"
        )
        
        if async_processing:
            # Queue task for async processing
            task = generate_visualization_task.delay(
                image_id=request.image_id,
                procedure_id=request.procedure_id,
                patient_id=request.patient_id,
            )
            
            return {
                "task_id": task.id,
                "status": "processing",
                "message": "Visualization generation started. Use task_id to track progress.",
                "status_url": f"/api/tasks/{task.id}/status",
                "websocket_url": f"/api/ws/tasks/{task.id}",
            }
        else:
            # Process synchronously
            result = await visualization_service.generate_surgical_preview(
                image_id=request.image_id,
                procedure_id=request.procedure_id,
                patient_id=request.patient_id,
            )
            
            # Convert datetime to string for response
            if result.get("generated_at"):
                result["generated_at"] = result["generated_at"].isoformat()
            
            # Return in the format expected by the frontend:
            # { id, status, visualization }
            return {
                "id": result["id"],
                "status": "completed",
                "visualization": VisualizationResult(**result)
            }
        
    except VisualizationError as e:
        error_msg = str(e) if str(e) else "Visualization generation failed"
        logger.error(f"Visualization error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = str(e) if str(e) else "Internal server error"
        logger.error(f"Unexpected error creating visualization: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/{visualization_id}")
async def get_visualization(
    visualization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get visualization by ID.
    
    Requirements: 1.3
    """
    try:
        logger.info(f"Retrieving visualization {visualization_id} for user {current_user.id}")
        
        result = await visualization_service.get_visualization(visualization_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Visualization not found")
        
        # Convert datetime to string for response
        if result.get("generated_at"):
            result["generated_at"] = result["generated_at"].isoformat()
        
        # Return in the format expected by the frontend for polling:
        # { id, status, visualization }
        return {
            "id": result["id"],
            "status": "completed",
            "visualization": VisualizationResult(**result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving visualization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{visualization_id}")
async def delete_visualization(
    visualization_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a visualization by ID.
    """
    try:
        from app.db.base import get_db, Collections
        
        logger.info(f"Deleting visualization {visualization_id} for user {current_user.id}")
        
        db = get_db()
        doc_ref = db.collection(Collections.VISUALIZATIONS).document(visualization_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Visualization not found")
        
        # Delete the document
        doc_ref.delete()
        
        logger.info(f"Successfully deleted visualization {visualization_id}")
        return {"message": "Visualization deleted successfully", "id": visualization_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting visualization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{visualization_id}/similar", response_model=SimilarCasesResponse)
async def find_similar_cases(
    visualization_id: str,
    procedure_type: Optional[str] = Query(None, description="Filter by procedure type"),
    age_range: Optional[str] = Query(None, description="Filter by age range (e.g., '20-30')"),
    min_outcome_rating: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum outcome rating"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user)
) -> SimilarCasesResponse:
    """
    Find similar surgical cases.
    
    This endpoint searches for similar cases based on visual similarity and filters.
    
    Requirements: 5.2, 5.3, 5.4, 5.5
    """
    try:
        logger.info(
            f"Finding similar cases for visualization {visualization_id}, "
            f"filters: procedure_type={procedure_type}, age_range={age_range}, "
            f"min_outcome_rating={min_outcome_rating}, limit={limit}"
        )
        
        # Find similar cases
        similar_cases = await visualization_service.find_similar_cases(
            visualization_id=visualization_id,
            procedure_type=procedure_type,
            age_range=age_range,
            min_outcome_rating=min_outcome_rating,
            limit=limit,
        )
        
        # Build response
        filters_applied = {}
        if procedure_type:
            filters_applied["procedure_type"] = procedure_type
        if age_range:
            filters_applied["age_range"] = age_range
        if min_outcome_rating is not None:
            filters_applied["min_outcome_rating"] = min_outcome_rating
        
        response = SimilarCasesResponse(
            query_visualization_id=visualization_id,
            similar_cases=[SimilarCase(**case) for case in similar_cases],
            total_found=len(similar_cases),
            filters_applied=filters_applied,
        )
        
        return response
        
    except VisualizationError as e:
        logger.error(f"Error finding similar cases: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error finding similar cases: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/compare")
async def compare_procedures(
    request: ComparisonRequest,
    async_processing: bool = Query(False, description="Process asynchronously using Celery"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare multiple procedures side-by-side.
    
    This endpoint generates visualizations for multiple procedures using the same
    source image and calculates cost, recovery time, and risk differences.
    
    If async_processing=true, returns a task_id that can be used to track progress.
    If async_processing=false, waits for completion and returns the result.
    
    Requirements: 4.1, 4.4, 9.5
    """
    try:
        logger.info(
            f"Creating comparison for user {current_user.id}, "
            f"image {request.source_image_id}, procedures {request.procedure_ids}, "
            f"async={async_processing}"
        )
        
        if async_processing:
            # Queue task for async processing
            task = generate_comparison_task.delay(
                image_id=request.source_image_id,
                procedure_ids=request.procedure_ids,
                patient_id=request.patient_id,
            )
            
            return {
                "task_id": task.id,
                "status": "processing",
                "message": "Comparison generation started. Use task_id to track progress.",
                "status_url": f"/api/tasks/{task.id}/status",
                "websocket_url": f"/api/ws/tasks/{task.id}",
            }
        else:
            # Process synchronously
            result = await comparison_service.create_comparison(
                source_image_id=request.source_image_id,
                procedure_ids=request.procedure_ids,
                patient_id=request.patient_id,
            )
            
            # Convert datetime to string for response
            if result.get("created_at"):
                result["created_at"] = result["created_at"].isoformat()
            
            return ComparisonResult(**result)
        
    except ComparisonError as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating comparison: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/comparisons/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison(
    comparison_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ComparisonResponse:
    """
    Get comparison by ID.
    
    This endpoint retrieves a previously created comparison with all its
    visualizations and difference calculations.
    
    Requirements: 4.4
    """
    try:
        logger.info(f"Retrieving comparison {comparison_id} for user {current_user.id}")
        
        result = await comparison_service.get_comparison(comparison_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        # Convert datetime to string for response
        if result.get("created_at"):
            result["created_at"] = result["created_at"].isoformat()
        
        return ComparisonResponse(comparison=ComparisonResult(**result))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving comparison: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/analyze-similarity-urls")
async def analyze_similarity_from_urls(
    ai_image_url: str,
    real_image_url: str,
    procedure_name: str = "the procedure",
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze similarity between two images given their URLs.
    
    This endpoint is designed for frontend auto-analysis when real result is uploaded.
    """
    try:
        logger.info(f"Analyzing similarity from URLs for {procedure_name}")
        
        analysis = await visualization_service.analyze_similarity_from_urls(
            ai_image_url=ai_image_url,
            real_image_url=real_image_url,
            procedure_name=procedure_name
        )
        
        return {"analysis": analysis}
        
    except VisualizationError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
