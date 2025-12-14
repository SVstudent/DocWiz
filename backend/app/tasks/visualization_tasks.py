"""Celery tasks for surgical visualization generation."""
import logging
from typing import Dict, Any

from app.celery_app import celery_app
from app.services.visualization_service import VisualizationService
from app.services.gemini_client import GeminiClient
from app.services.storage_service import StorageService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.visualization_tasks.generate_visualization")
def generate_visualization_task(
    self,
    image_id: str,
    procedure_id: str,
    patient_id: str = None,
) -> Dict[str, Any]:
    """
    Celery task for generating surgical visualization.
    
    This is a long-running operation that:
    1. Retrieves source image from storage
    2. Calls Gemini API for image generation
    3. Stores result images
    4. Generates embeddings
    5. Saves to database
    
    Args:
        self: Celery task instance (for updating state)
        image_id: ID of the uploaded source image
        procedure_id: ID of the surgical procedure
        patient_id: Optional patient profile ID
        
    Returns:
        Dictionary containing visualization result
    """
    try:
        # Update task state to indicate processing has started
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Initializing visualization generation",
                "progress": 0,
                "image_id": image_id,
                "procedure_id": procedure_id,
            }
        )
        
        # Initialize services
        visualization_service = VisualizationService(
            gemini_client=GeminiClient(),
            storage_service=StorageService(),
            embedding_service=EmbeddingService(),
            qdrant_client=QdrantClient(),
        )
        
        # Update progress
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Generating surgical preview with AI",
                "progress": 20,
            }
        )
        
        # Generate visualization (this is async, but Celery tasks are sync)
        # We need to run it in an event loop
        import asyncio
        result = asyncio.run(
            visualization_service.generate_surgical_preview(
                image_id=image_id,
                procedure_id=procedure_id,
                patient_id=patient_id,
            )
        )
        
        # Update progress
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Storing results and generating embeddings",
                "progress": 80,
            }
        )
        
        logger.info(f"Visualization generated successfully: {result.get('id')}")
        
        return {
            "status": "completed",
            "result": result,
            "progress": 100,
        }
        
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Failed to generate visualization",
                "error": str(e),
                "progress": 0,
            }
        )
        raise


@celery_app.task(bind=True, name="app.tasks.visualization_tasks.generate_comparison")
def generate_comparison_task(
    self,
    image_id: str,
    procedure_ids: list[str],
    patient_id: str = None,
) -> Dict[str, Any]:
    """
    Celery task for generating multi-procedure comparison.
    
    Args:
        self: Celery task instance
        image_id: ID of the source image
        procedure_ids: List of procedure IDs to compare
        patient_id: Optional patient profile ID
        
    Returns:
        Dictionary containing comparison result
    """
    try:
        self.update_state(
            state="PROCESSING",
            meta={
                "status": "Generating comparison visualizations",
                "progress": 0,
                "total_procedures": len(procedure_ids),
            }
        )
        
        from app.services.comparison_service import ComparisonService
        comparison_service = ComparisonService()
        
        # Generate comparison
        import asyncio
        result = asyncio.run(
            comparison_service.generate_comparison(
                image_id=image_id,
                procedure_ids=procedure_ids,
                patient_id=patient_id,
            )
        )
        
        return {
            "status": "completed",
            "result": result,
            "progress": 100,
        }
        
    except Exception as e:
        logger.error(f"Error generating comparison: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={
                "status": "Failed to generate comparison",
                "error": str(e),
            }
        )
        raise
