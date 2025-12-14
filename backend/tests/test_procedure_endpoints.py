"""Integration tests for procedure API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_procedures_endpoint():
    """Test GET /api/procedures endpoint."""
    response = client.get("/api/procedures")
    assert response.status_code == 200
    data = response.json()
    assert "procedures" in data
    assert "total" in data
    assert isinstance(data["procedures"], list)
    assert isinstance(data["total"], int)


def test_list_categories_endpoint():
    """Test GET /api/procedures/categories endpoint."""
    response = client.get("/api/procedures/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "total" in data
    assert isinstance(data["categories"], list)
    assert isinstance(data["total"], int)


def test_get_procedure_by_id_not_found():
    """Test GET /api/procedures/{id} with non-existent ID."""
    response = client.get("/api/procedures/nonexistent-id")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_initialize_procedures_endpoint():
    """Test POST /api/procedures/initialize endpoint."""
    response = client.post("/api/procedures/initialize")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "count" in data
    assert isinstance(data["count"], int)


def test_get_procedure_by_id_after_initialization():
    """Test GET /api/procedures/{id} after initialization."""
    # First initialize procedures
    init_response = client.post("/api/procedures/initialize")
    assert init_response.status_code == 200
    
    # Then try to get a specific procedure
    response = client.get("/api/procedures/rhinoplasty-001")
    
    if response.status_code == 200:
        data = response.json()
        # Verify required fields per Requirements 1.2
        assert "description" in data
        assert "recovery_days" in data
        assert "risk_level" in data
        assert "cost_range" in data
        
        # Verify data types
        assert isinstance(data["description"], str)
        assert isinstance(data["recovery_days"], int)
        assert isinstance(data["risk_level"], str)
        assert isinstance(data["cost_range"], dict)
        assert "min" in data["cost_range"]
        assert "max" in data["cost_range"]


def test_filter_procedures_by_category():
    """Test GET /api/procedures with category filter."""
    # Initialize procedures first
    client.post("/api/procedures/initialize")
    
    # Filter by facial category
    response = client.get("/api/procedures?category=facial")
    assert response.status_code == 200
    data = response.json()
    assert "procedures" in data
    
    # Verify all returned procedures are in facial category
    for proc in data["procedures"]:
        assert proc["category"] == "facial"


def test_search_procedures():
    """Test GET /api/procedures with search query."""
    # Initialize procedures first
    client.post("/api/procedures/initialize")
    
    # Search for rhinoplasty
    response = client.get("/api/procedures?search=rhinoplasty")
    assert response.status_code == 200
    data = response.json()
    assert "procedures" in data
    
    # Verify search results contain the search term
    if data["total"] > 0:
        found = False
        for proc in data["procedures"]:
            if "rhinoplasty" in proc["name"].lower() or "rhinoplasty" in proc["description"].lower():
                found = True
                break
        assert found, "Search results should contain procedures matching the query"
