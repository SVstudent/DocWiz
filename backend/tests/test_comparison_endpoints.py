"""Integration tests for comparison API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime

from app.main import app
from app.db.models import User
from app.api.dependencies import get_current_active_user


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    return user


@pytest.fixture
def test_client(mock_user):
    """Create test client with mocked authentication."""
    # Override the authentication dependency
    async def override_get_current_active_user():
        return mock_user
    
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    
    with TestClient(app) as client:
        yield client
    
    # Clear overrides after test
    app.dependency_overrides.clear()


def test_create_comparison_endpoint(test_client):
    """Test POST /api/visualizations/compare endpoint."""
    # Setup mock
    comparison_id = str(uuid.uuid4())
    source_image_id = str(uuid.uuid4())
    
    mock_comparison_result = {
        "id": comparison_id,
        "source_image_id": source_image_id,
        "patient_id": None,
        "procedures": [
            {
                "procedure_id": "rhinoplasty-001",
                "procedure_name": "Rhinoplasty",
                "visualization_id": str(uuid.uuid4()),
                "before_image_url": f"https://storage.example.com/images/{source_image_id}",
                "after_image_url": f"https://storage.example.com/images/{uuid.uuid4()}",
                "cost": 10000.0,
                "recovery_days": 14,
                "risk_level": "medium",
            },
            {
                "procedure_id": "facelift-001",
                "procedure_name": "Facelift",
                "visualization_id": str(uuid.uuid4()),
                "before_image_url": f"https://storage.example.com/images/{source_image_id}",
                "after_image_url": f"https://storage.example.com/images/{uuid.uuid4()}",
                "cost": 20000.0,
                "recovery_days": 28,
                "risk_level": "high",
            },
        ],
        "cost_differences": {
            "Rhinoplasty_vs_Facelift": 10000.0
        },
        "recovery_differences": {
            "Rhinoplasty_vs_Facelift": 14
        },
        "risk_differences": {
            "Rhinoplasty_vs_Facelift": "Facelift has higher risk (high vs medium)"
        },
        "created_at": datetime.utcnow(),
        "metadata": {
            "procedure_count": 2,
            "procedure_ids": ["rhinoplasty-001", "facelift-001"],
        },
    }
    
    with patch('app.api.routes.visualizations.comparison_service') as mock_service:
        mock_service.create_comparison = AsyncMock(return_value=mock_comparison_result)
        
        # Make request
        response = test_client.post(
            "/api/visualizations/compare",
            json={
                "source_image_id": source_image_id,
                "procedure_ids": ["rhinoplasty-001", "facelift-001"],
                "patient_id": None,
            }
        )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == comparison_id
    assert data["source_image_id"] == source_image_id
    assert len(data["procedures"]) == 2
    assert "cost_differences" in data
    assert "recovery_differences" in data
    assert "risk_differences" in data


def test_get_comparison_endpoint(test_client):
    """Test GET /api/visualizations/comparisons/{comparison_id} endpoint."""
    # Setup mock
    comparison_id = str(uuid.uuid4())
    source_image_id = str(uuid.uuid4())
    
    mock_comparison_result = {
        "id": comparison_id,
        "source_image_id": source_image_id,
        "patient_id": None,
        "procedures": [
            {
                "procedure_id": "rhinoplasty-001",
                "procedure_name": "Rhinoplasty",
                "visualization_id": str(uuid.uuid4()),
                "before_image_url": f"https://storage.example.com/images/{source_image_id}",
                "after_image_url": f"https://storage.example.com/images/{uuid.uuid4()}",
                "cost": 10000.0,
                "recovery_days": 14,
                "risk_level": "medium",
            },
        ],
        "cost_differences": {},
        "recovery_differences": {},
        "risk_differences": {},
        "created_at": datetime.utcnow(),
        "metadata": {},
    }
    
    with patch('app.api.routes.visualizations.comparison_service') as mock_service:
        mock_service.get_comparison = AsyncMock(return_value=mock_comparison_result)
        
        # Make request
        response = test_client.get(f"/api/visualizations/comparisons/{comparison_id}")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "comparison" in data
    assert data["comparison"]["id"] == comparison_id
    assert data["comparison"]["source_image_id"] == source_image_id


def test_get_comparison_not_found(test_client):
    """Test GET /api/visualizations/comparisons/{comparison_id} with non-existent ID."""
    comparison_id = str(uuid.uuid4())
    
    with patch('app.api.routes.visualizations.comparison_service') as mock_service:
        # Setup mock to return None
        mock_service.get_comparison = AsyncMock(return_value=None)
        
        # Make request
        response = test_client.get(f"/api/visualizations/comparisons/{comparison_id}")
    
    # Assertions
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_comparison_with_insufficient_procedures(test_client):
    """Test POST /api/visualizations/compare with less than 2 procedures."""
    source_image_id = str(uuid.uuid4())
    
    # Make request with only 1 procedure (should fail Pydantic validation)
    response = test_client.post(
        "/api/visualizations/compare",
        json={
            "source_image_id": source_image_id,
            "procedure_ids": ["rhinoplasty-001"],  # Only 1 procedure
            "patient_id": None,
        }
    )
    
    # Assertions - Pydantic validation returns 422 for invalid input
    assert response.status_code == 422
    # Check that the error mentions the procedure_ids field
    data = response.json()
    assert "detail" in data
    # The error should be about procedure_ids validation
    error_details = str(data["detail"]).lower()
    assert "procedure_ids" in error_details or "at least" in error_details
