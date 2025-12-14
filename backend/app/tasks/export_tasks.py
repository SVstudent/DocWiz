"""Celery tasks for export generation."""
import logging
from typing import Dict, Any, List

from app.celery_app import celery_app
from app.services.export_service import ExportService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.export_tasks.generate_export")
def generate_export_task(
    self,
    patient_id: str,
    visualization_ids: List[str],
    format: str = "pdf",
    shareable: bool = False,
) -> Dict[str, Any]:
    """
    Celery task for generating comprehensive export report.
    
    This is a long-running operation that:
    1. Gathers all patient data
    2. Generates comprehensive report
    3. Stores export file
    
    Args:
        self: Celery task instance
        patient_id: Patient profile ID
        visualization_ids: List of visualization IDs to include
        format: Export format (pdf, png, jpeg, json)
        shareable: Whether to create shareable version (removes sensitive data)
        
    Returns:
        Dictionary containing export result
    """
    try:
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Gathering patient data",
                "progress": 10,
            }
        )
        
        export_service = ExportService()
        
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Generating comprehensive report",
                "progress": 30,
            }
        )
        
        # Generate export
        import asyncio
        if shareable:
            result = asyncio.run(
                export_service.export_shareable_version(
                    patient_id=patient_id,
                    visualization_ids=visualization_ids,
                    format=format,
                )
            )
        else:
            result = asyncio.run(
                export_service.export_comprehensive_report(
                    patient_id=patient_id,
                    visualization_ids=visualization_ids,
                    format=format,
                )
            )
        
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Finalizing export",
                "progress": 90,
            }
        )
        
        logger.info(f"Export generated successfully: {result.get('id')}")
        
        return {
            "status": "completed",
            "result": result,
            "progress": 100,
        }
        
    except Exception as e:
        logger.error(f"Error generating export: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Failed to generate export",
                "error": str(e),
            }
        )
        raise


@celery_app.task(bind=True, name="app.tasks.export_tasks.generate_cost_infographic")
def generate_cost_infographic_task(
    self,
    cost_breakdown_id: str,
    format: str = "png",
) -> Dict[str, Any]:
    """
    Celery task for generating cost infographic.
    
    Args:
        self: Celery task instance
        cost_breakdown_id: ID of the cost breakdown
        format: Image format (png or jpeg)
        
    Returns:
        Dictionary containing infographic result
    """
    try:
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Generating cost infographic",
                "progress": 20,
            }
        )
        
        from app.services.cost_estimation_service import CostEstimationService
        cost_service = CostEstimationService()
        
        # Generate infographic
        import asyncio
        result = asyncio.run(
            cost_service.generate_cost_infographic(
                cost_breakdown_id=cost_breakdown_id,
                format=format,
            )
        )
        
        return {
            "status": "completed",
            "result": result,
            "progress": 100,
        }
        
    except Exception as e:
        logger.error(f"Error generating cost infographic: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Failed to generate cost infographic",
                "error": str(e),
            }
        )
        raise
