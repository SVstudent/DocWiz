"""Export and report generation routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
import io

from app.api.dependencies import get_current_active_user, get_firestore_db
from app.db.models import User
from app.schemas.export import ExportRequest, ExportResponse, ExportMetadata
from app.services.export_service import get_export_service
from app.tasks.export_tasks import generate_export_task
from google.cloud.firestore_v1 import Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("")
async def create_export(
    request: ExportRequest,
    async_processing: bool = Query(False, description="Process asynchronously using Celery"),
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Create a comprehensive export report.
    
    Generates a report including:
    - All visualizations (or specified ones)
    - Cost breakdowns (or specified ones)
    - Comparison analysis (or specified ones)
    - Medical disclaimers
    
    Supports multiple formats: PDF, PNG, JPEG, JSON
    
    If async_processing=true, returns a task_id that can be used to track progress.
    If async_processing=false, waits for completion and returns the result.
    
    Requirements: 10.1, 10.2, 9.5
    """
    try:
        logger.info(
            f"Creating export for patient {request.patient_id}, "
            f"format={request.format}, async={async_processing}"
        )
        
        if async_processing:
            # Queue task for async processing
            task = generate_export_task.delay(
                patient_id=request.patient_id,
                visualization_ids=request.visualization_ids or [],
                format=request.format,
                shareable=request.shareable,
            )
            
            return {
                "task_id": task.id,
                "status": "processing",
                "message": "Export generation started. Use task_id to track progress.",
                "status_url": f"/api/tasks/{task.id}/status",
                "websocket_url": f"/api/ws/tasks/{task.id}",
            }
        else:
            # Process synchronously
            export_service = get_export_service(db)
            
            # Generate export
            export_bytes = await export_service.export_comprehensive_report(
                patient_id=request.patient_id,
                format=request.format,
                shareable=request.shareable,
                include_visualizations=request.include_visualizations,
                include_cost_estimates=request.include_cost_estimates,
                include_comparisons=request.include_comparisons,
                visualization_ids=request.visualization_ids,
                cost_breakdown_ids=request.cost_breakdown_ids,
                comparison_ids=request.comparison_ids,
            )
            
            # Create metadata
            metadata = await export_service.create_export_metadata(
                patient_id=request.patient_id,
                format=request.format,
                shareable=request.shareable,
                file_size_bytes=len(export_bytes),
            )
            
            # In production, upload to storage and generate download URL
            # For now, we'll return metadata with a placeholder URL
            download_url = f"/api/exports/{metadata.id}/download"
            
            return ExportResponse(
                id=metadata.id,
                patient_id=metadata.patient_id,
                patient_name=metadata.patient_name,
                format=metadata.format,
                shareable=metadata.shareable,
                created_at=metadata.created_at,
                status="completed",
                download_url=download_url,
            )
        
    except ValueError as e:
        logger.error(f"Validation error creating export: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating export: {e}")
        raise HTTPException(status_code=500, detail="Failed to create export")


@router.get("/{export_id}", response_model=ExportMetadata)
async def get_export_metadata(
    export_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Get export metadata.
    
    Returns information about an export including:
    - Patient information
    - Format
    - Creation timestamp
    - File size
    """
    try:
        export_service = get_export_service(db)
        metadata = await export_service.get_export_metadata(export_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Export {export_id} not found")
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving export metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve export metadata")


@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Download export file.
    
    Returns the export file in the requested format.
    """
    try:
        export_service = get_export_service(db)
        
        # Get metadata
        metadata = await export_service.get_export_metadata(export_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Export {export_id} not found")
        
        # Regenerate export (in production, this would fetch from storage)
        export_bytes = await export_service.export_comprehensive_report(
            patient_id=metadata.patient_id,
            format=metadata.format,
            shareable=metadata.shareable,
        )
        
        # Determine content type and filename
        content_types = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpeg": "image/jpeg",
            "json": "application/json",
        }
        
        extensions = {
            "pdf": "pdf",
            "png": "png",
            "jpeg": "jpg",
            "json": "json",
        }
        
        content_type = content_types.get(metadata.format, "application/octet-stream")
        extension = extensions.get(metadata.format, "bin")
        filename = f"docwiz_report_{export_id}.{extension}"
        
        # Return file
        return Response(
            content=export_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        raise HTTPException(status_code=500, detail="Failed to download export")
