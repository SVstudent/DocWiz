"""API routes for Celery task management."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.task_service import TaskService

router = APIRouter(tags=["tasks"])
task_service = TaskService()


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status information including state, progress, and result
    """
    try:
        status = task_service.get_task_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a running Celery task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Cancellation status
    """
    try:
        result = task_service.cancel_task(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")


@router.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> Dict[str, Any]:
    """
    Get the result of a completed task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task result if available
    """
    try:
        result = task_service.get_task_result(task_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Task result not available. Task may still be running or failed."
            )
        return {"task_id": task_id, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task result: {str(e)}")
