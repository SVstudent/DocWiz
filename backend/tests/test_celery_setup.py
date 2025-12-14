"""Tests for Celery async task processing setup."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.services.task_service import TaskService


class TestCeleryConfiguration:
    """Test Celery application configuration."""

    def test_celery_app_exists(self):
        """Test that Celery app is properly configured."""
        assert celery_app is not None
        assert celery_app.conf.broker_url is not None
        assert celery_app.conf.result_backend is not None

    def test_celery_broker_configured(self):
        """Test that Redis broker is configured."""
        assert "redis://" in celery_app.conf.broker_url

    def test_celery_backend_configured(self):
        """Test that Redis result backend is configured."""
        assert "redis://" in celery_app.conf.result_backend

    def test_celery_serializer_configured(self):
        """Test that JSON serializer is configured."""
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert "json" in celery_app.conf.accept_content

    def test_celery_timezone_configured(self):
        """Test that timezone is configured."""
        assert celery_app.conf.timezone == "UTC"
        assert celery_app.conf.enable_utc is True

    def test_celery_task_limits_configured(self):
        """Test that task time limits are configured."""
        assert celery_app.conf.task_time_limit == 300  # 5 minutes
        assert celery_app.conf.task_soft_time_limit == 240  # 4 minutes

    def test_celery_task_tracking_enabled(self):
        """Test that task tracking is enabled."""
        assert celery_app.conf.task_track_started is True
        assert celery_app.conf.task_acks_late is True


class TestCeleryTasks:
    """Test Celery task registration."""

    def test_visualization_task_registered(self):
        """Test that visualization task is registered."""
        task_name = "app.tasks.visualization_tasks.generate_visualization"
        assert task_name in celery_app.tasks

    def test_comparison_task_registered(self):
        """Test that comparison task is registered."""
        task_name = "app.tasks.visualization_tasks.generate_comparison"
        assert task_name in celery_app.tasks

    def test_export_task_registered(self):
        """Test that export task is registered."""
        task_name = "app.tasks.export_tasks.generate_export"
        assert task_name in celery_app.tasks

    def test_cost_infographic_task_registered(self):
        """Test that cost infographic task is registered."""
        task_name = "app.tasks.export_tasks.generate_cost_infographic"
        assert task_name in celery_app.tasks

    def test_all_custom_tasks_registered(self):
        """Test that all custom tasks are registered."""
        custom_tasks = [
            task for task in celery_app.tasks.keys()
            if task.startswith("app.tasks")
        ]
        assert len(custom_tasks) == 4


class TestTaskService:
    """Test TaskService for task status tracking."""

    @patch('app.services.task_service.AsyncResult')
    def test_get_task_status_pending(self, mock_async_result):
        """Test getting status of pending task."""
        # Mock task result
        mock_result = Mock()
        mock_result.state = "PENDING"
        mock_result.ready.return_value = False
        mock_result.successful.return_value = False
        mock_async_result.return_value = mock_result

        # Get status
        status = TaskService.get_task_status("test-task-id")

        # Verify
        assert status["task_id"] == "test-task-id"
        assert status["state"] == "PENDING"
        assert status["ready"] is False
        assert status["progress"] == 0

    @patch('app.services.task_service.AsyncResult')
    def test_get_task_status_processing(self, mock_async_result):
        """Test getting status of processing task."""
        # Mock task result
        mock_result = Mock()
        mock_result.state = "PROCESSING"
        mock_result.ready.return_value = False
        mock_result.info = {
            "status": "Generating visualization",
            "progress": 50,
        }
        mock_async_result.return_value = mock_result

        # Get status
        status = TaskService.get_task_status("test-task-id")

        # Verify
        assert status["state"] == "PROCESSING"
        assert status["progress"] == 50
        assert status["status"] == "Generating visualization"

    @patch('app.services.task_service.AsyncResult')
    def test_get_task_status_success(self, mock_async_result):
        """Test getting status of successful task."""
        # Mock task result
        mock_result = Mock()
        mock_result.state = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = {
            "status": "completed",
            "result": {"id": "viz-123"},
        }
        mock_async_result.return_value = mock_result

        # Get status
        status = TaskService.get_task_status("test-task-id")

        # Verify
        assert status["state"] == "SUCCESS"
        assert status["ready"] is True
        assert status["progress"] == 100
        assert status["result"]["id"] == "viz-123"

    @patch('app.services.task_service.AsyncResult')
    def test_get_task_status_failure(self, mock_async_result):
        """Test getting status of failed task."""
        # Mock task result
        mock_result = Mock()
        mock_result.state = "FAILURE"
        mock_result.ready.return_value = True
        mock_result.successful.return_value = False
        mock_result.info = Exception("Task failed")
        mock_async_result.return_value = mock_result

        # Get status
        status = TaskService.get_task_status("test-task-id")

        # Verify
        assert status["state"] == "FAILURE"
        assert status["progress"] == 0
        assert "Task failed" in status["error"]

    @patch('app.services.task_service.celery_app.control.revoke')
    def test_cancel_task(self, mock_revoke):
        """Test cancelling a task."""
        # Cancel task
        result = TaskService.cancel_task("test-task-id")

        # Verify
        assert result["task_id"] == "test-task-id"
        assert result["status"] == "cancelled"
        mock_revoke.assert_called_once_with("test-task-id", terminate=True)

    @patch('app.services.task_service.AsyncResult')
    def test_get_task_result_success(self, mock_async_result):
        """Test getting result of completed task."""
        # Mock task result
        mock_result = Mock()
        mock_result.ready.return_value = True
        mock_result.successful.return_value = True
        mock_result.result = {
            "status": "completed",
            "result": {"id": "viz-123", "url": "https://example.com/viz.jpg"},
        }
        mock_async_result.return_value = mock_result

        # Get result
        result = TaskService.get_task_result("test-task-id")

        # Verify
        assert result is not None
        assert result["id"] == "viz-123"

    @patch('app.services.task_service.AsyncResult')
    def test_get_task_result_not_ready(self, mock_async_result):
        """Test getting result of task that's not ready."""
        # Mock task result
        mock_result = Mock()
        mock_result.ready.return_value = False
        mock_async_result.return_value = mock_result

        # Get result
        result = TaskService.get_task_result("test-task-id")

        # Verify
        assert result is None


class TestTaskIntegration:
    """Integration tests for task execution (requires running worker)."""

    @pytest.mark.integration
    def test_task_can_be_queued(self):
        """Test that a task can be queued (not executed)."""
        from app.tasks.visualization_tasks import generate_visualization_task

        # Queue task (don't wait for result)
        result = generate_visualization_task.apply_async(
            args=["test-image-id", "test-procedure-id"],
            kwargs={"patient_id": "test-patient-id"},
        )

        # Verify task was queued
        assert result.id is not None
        assert isinstance(result, AsyncResult)

    @pytest.mark.integration
    def test_export_task_can_be_queued(self):
        """Test that export task can be queued."""
        from app.tasks.export_tasks import generate_export_task

        # Queue task
        result = generate_export_task.apply_async(
            args=["test-patient-id", ["viz-1", "viz-2"]],
            kwargs={"format": "pdf", "shareable": False},
        )

        # Verify task was queued
        assert result.id is not None
        assert isinstance(result, AsyncResult)


class TestTaskRoutes:
    """Test task management API routes."""

    def test_task_routes_exist(self):
        """Test that task routes are registered."""
        from app.main import app

        routes = [route.path for route in app.routes if hasattr(route, "path")]

        assert "/api/tasks/{task_id}/status" in routes
        assert "/api/tasks/{task_id}/cancel" in routes
        assert "/api/tasks/{task_id}/result" in routes

    def test_websocket_route_exists(self):
        """Test that WebSocket route is registered."""
        from app.main import app

        routes = [route.path for route in app.routes if hasattr(route, "path")]

        assert "/api/ws/tasks/{task_id}" in routes


class TestVisualizationRouteAsyncSupport:
    """Test that visualization routes support async processing."""

    def test_visualization_route_has_async_parameter(self):
        """Test that visualization endpoint accepts async_processing parameter."""
        from app.api.routes.visualizations import create_visualization
        import inspect

        # Get function signature
        sig = inspect.signature(create_visualization)

        # Check for async_processing parameter
        params = sig.parameters
        assert "async_processing" in params

    def test_comparison_route_has_async_parameter(self):
        """Test that comparison endpoint accepts async_processing parameter."""
        from app.api.routes.visualizations import compare_procedures
        import inspect

        # Get function signature
        sig = inspect.signature(compare_procedures)

        # Check for async_processing parameter
        params = sig.parameters
        assert "async_processing" in params


class TestExportRouteAsyncSupport:
    """Test that export routes support async processing."""

    def test_export_route_has_async_parameter(self):
        """Test that export endpoint accepts async_processing parameter."""
        from app.api.routes.exports import create_export
        import inspect

        # Get function signature
        sig = inspect.signature(create_export)

        # Check for async_processing parameter
        params = sig.parameters
        assert "async_processing" in params
