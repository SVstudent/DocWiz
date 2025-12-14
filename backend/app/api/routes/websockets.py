"""WebSocket routes for real-time task progress updates."""
import asyncio
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.task_service import TaskService

router = APIRouter(tags=["websockets"])
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for task progress updates."""

    def __init__(self):
        self.active_connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection for a task."""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket connected for task {task_id}")

    def disconnect(self, task_id: str, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if task_id in self.active_connections:
            self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
        logger.info(f"WebSocket disconnected for task {task_id}")

    async def send_update(self, task_id: str, message: Dict[str, Any]):
        """Send an update to all connections for a task."""
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {str(e)}")


manager = ConnectionManager()
task_service = TaskService()


@router.websocket("/ws/tasks/{task_id}")
async def task_progress_websocket(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time task progress updates.
    
    Clients can connect to this endpoint to receive real-time updates
    about task progress, status changes, and completion.
    
    Args:
        websocket: WebSocket connection
        task_id: Celery task ID to monitor
    """
    await manager.connect(task_id, websocket)
    
    try:
        # Send initial status
        initial_status = task_service.get_task_status(task_id)
        await websocket.send_json({
            "type": "status",
            "data": initial_status,
        })
        
        # Poll for updates and send to client
        while True:
            # Get current task status
            status = task_service.get_task_status(task_id)
            
            # Send status update
            await websocket.send_json({
                "type": "status",
                "data": status,
            })
            
            # If task is complete or failed, send final message and close
            if status["state"] in ["SUCCESS", "FAILURE", "REVOKED"]:
                await websocket.send_json({
                    "type": "complete",
                    "data": status,
                })
                break
            
            # Wait before next poll (1 second)
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
    finally:
        manager.disconnect(task_id, websocket)
