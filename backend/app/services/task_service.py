"""Service for tracking Celery task status."""
import logging
from typing import Dict, Any, Optional
from celery.result import AsyncResult

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing and tracking Celery tasks."""

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """
        Get the status of a Celery task.
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Dictionary containing task status information
        """
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "state": task_result.state,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else None,
        }
        
        # Add task-specific information based on state
        if task_result.state == "PENDING":
            response["status"] = "Task is waiting to be processed"
            response["progress"] = 0
            
        elif task_result.state == "PROCESSING":
            # Custom state we set in tasks
            info = task_result.info or {}
            response["status"] = info.get("status", "Processing")
            response["progress"] = info.get("progress", 0)
            response["meta"] = info
            
        elif task_result.state == "SUCCESS":
            result = task_result.result or {}
            response["status"] = "Task completed successfully"
            response["progress"] = 100
            response["result"] = result.get("result")
            
        elif task_result.state == "FAILURE":
            response["status"] = "Task failed"
            response["progress"] = 0
            response["error"] = str(task_result.info)
            
        elif task_result.state == "RETRY":
            response["status"] = "Task is being retried"
            response["progress"] = 0
            
        elif task_result.state == "REVOKED":
            response["status"] = "Task was cancelled"
            response["progress"] = 0
            
        else:
            response["status"] = f"Unknown state: {task_result.state}"
            response["progress"] = 0
            
        return response

    @staticmethod
    def cancel_task(task_id: str) -> Dict[str, Any]:
        """
        Cancel a running Celery task.
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Dictionary containing cancellation status
        """
        try:
            celery_app.control.revoke(task_id, terminate=True)
            return {
                "task_id": task_id,
                "status": "cancelled",
                "message": "Task cancellation requested",
            }
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {str(e)}")
            return {
                "task_id": task_id,
                "status": "error",
                "message": f"Failed to cancel task: {str(e)}",
            }

    @staticmethod
    def get_task_result(task_id: str) -> Optional[Any]:
        """
        Get the result of a completed task.
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Task result if available, None otherwise
        """
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready() and task_result.successful():
            result = task_result.result
            if isinstance(result, dict):
                return result.get("result")
            return result
            
        return None
