"""Property-based tests for search result completeness.

Feature: docwiz-surgical-platform, Property 18: Search result completeness

For any similar case in search results, the result should include anonymized
before/after images, outcome rating, and patient satisfaction score.

Validates: Requirements 5.3
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.services.visualization_service import VisualizationService


# Custom strategies for test data
@st.composite
def similar_case_payload_strategy(draw):
    """Generate a similar case payload from Qdrant."""
    viz_id = str(uuid.uuid4())
    return {
        "id": viz_id,
        "score": draw(st.floats(min_value=0.0, max_value=1.0)),
        "payload": {
            "visualization_id": viz_id,
            "procedure_type": draw(st.sampled_from(["facial", "body", "reconstructive"])),
            "age_range": draw(st.sampled_from(["20-30", "30-40", "40-50", "50-60"])),
            "outcome_rating": draw(st.floats(min_value=0.0, max_value=1.0)),
            "patient_id": f"patient_{draw(st.integers(min_value=1, max_value=1000))}",
            "created_at": "2024-01-01T00:00:00",
        }
    }


@st.composite
def visualization_data_strategy(draw, viz_id: str):
    """Generate visualization data for a given ID."""
    return {
        "id": viz_id,
        "patient_id": f"patient_{draw(st.integers(min_value=1, max_value=1000))}",
        "procedure_id": f"proc_{draw(st.integers(min_value=1, max_value=100))}",
        "procedure_name": draw(st.sampled_from(["Rhinoplasty", "Breast Augmentation", "Facelift"])),
        "before_image_url": f"https://storage.example.com/before_{viz_id}.jpg",
        "after_image_url": f"https://storage.example.com/after_{viz_id}.jpg",
        "prompt_used": draw(st.text(min_size=10, max_size=200)),
        "generated_at": "2024-01-01T00:00:00",
        "confidence_score": draw(st.floats(min_value=0.0, max_value=1.0)),
        "metadata": {},
    }


@pytest.mark.asyncio
@given(
    similar_results=st.lists(
        similar_case_payload_strategy(),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100, deadline=None)
async def test_search_result_completeness(similar_results):
    """
    Feature: docwiz-surgical-platform, Property 18: Search result completeness
    
    For any similar case in search results, the result should include anonymized
    before/after images, outcome rating, and patient satisfaction score.
    
    Validates: Requirements 5.3
    """
    # Create service with mocked dependencies
    service = VisualizationService()
    
    # Mock the embedding service to return our test data
    service.embedding_service.find_similar_cases = AsyncMock(return_value=similar_results)
    
    # Mock get_visualization to return visualization data for each result
    async def mock_get_visualization(viz_id):
        # Find the matching result
        for result in similar_results:
            if result["payload"]["visualization_id"] == viz_id:
                # Generate visualization data
                return {
                    "id": viz_id,
                    "patient_id": result["payload"]["patient_id"],
                    "procedure_id": "test_procedure",
                    "procedure_name": "Test Procedure",
                    "before_image_url": f"https://storage.example.com/before_{viz_id}.jpg",
                    "after_image_url": f"https://storage.example.com/after_{viz_id}.jpg",
                    "prompt_used": "test prompt",
                    "generated_at": "2024-01-01T00:00:00",
                    "confidence_score": 0.85,
                    "metadata": {},
                }
        return None
    
    service.get_visualization = mock_get_visualization
    
    # Mock the initial visualization lookup
    query_viz_id = str(uuid.uuid4())
    query_viz_data = {
        "id": query_viz_id,
        "before_image_url": "https://storage.example.com/query_before.jpg",
        "after_image_url": "https://storage.example.com/query_after.jpg",
        "procedure_id": "test_procedure",
        "procedure_name": "Test Procedure",
        "patient_id": "test_patient",
        "prompt_used": "test prompt",
        "generated_at": "2024-01-01T00:00:00",
        "confidence_score": 0.85,
        "metadata": {},
    }
    
    # Mock HTTP client to return image data
    mock_image_data = b"fake_image_data"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_image_data
        
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        # Override get_visualization for the query
        original_get_viz = service.get_visualization
        async def mock_get_viz_with_query(viz_id):
            if viz_id == query_viz_id:
                return query_viz_data
            return await original_get_viz(viz_id)
        
        service.get_visualization = mock_get_viz_with_query
        
        # Call find_similar_cases
        results = await service.find_similar_cases(
            visualization_id=query_viz_id,
            limit=len(similar_results)
        )
    
    # Property: For any similar case in search results, the result should include:
    # - anonymized before/after images
    # - outcome rating
    # - patient satisfaction score
    
    for result in results:
        # Check that before_image_url is present and non-empty
        assert "before_image_url" in result, "Result missing before_image_url"
        assert result["before_image_url"], "before_image_url is empty"
        assert isinstance(result["before_image_url"], str), "before_image_url is not a string"
        
        # Check that after_image_url is present and non-empty
        assert "after_image_url" in result, "Result missing after_image_url"
        assert result["after_image_url"], "after_image_url is empty"
        assert isinstance(result["after_image_url"], str), "after_image_url is not a string"
        
        # Check that outcome_rating is present and valid
        assert "outcome_rating" in result, "Result missing outcome_rating"
        assert isinstance(result["outcome_rating"], (int, float)), "outcome_rating is not numeric"
        assert 0.0 <= result["outcome_rating"] <= 1.0, "outcome_rating out of range [0.0, 1.0]"
        
        # Check that patient_satisfaction is present and valid
        assert "patient_satisfaction" in result, "Result missing patient_satisfaction"
        assert isinstance(result["patient_satisfaction"], int), "patient_satisfaction is not an integer"
        
        # Check that data is anonymized
        assert "anonymized" in result, "Result missing anonymized flag"
        assert result["anonymized"] is True, "Result is not marked as anonymized"


@pytest.mark.asyncio
async def test_search_result_completeness_empty_results():
    """Test that empty results are handled correctly."""
    service = VisualizationService()
    
    # Mock empty results
    service.embedding_service.find_similar_cases = AsyncMock(return_value=[])
    
    query_viz_id = str(uuid.uuid4())
    query_viz_data = {
        "id": query_viz_id,
        "before_image_url": "https://storage.example.com/query_before.jpg",
        "after_image_url": "https://storage.example.com/query_after.jpg",
        "procedure_id": "test_procedure",
        "procedure_name": "Test Procedure",
        "patient_id": "test_patient",
        "prompt_used": "test prompt",
        "generated_at": "2024-01-01T00:00:00",
        "confidence_score": 0.85,
        "metadata": {},
    }
    
    mock_image_data = b"fake_image_data"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_image_data
        
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        async def mock_get_viz(viz_id):
            if viz_id == query_viz_id:
                return query_viz_data
            return None
        
        service.get_visualization = mock_get_viz
        
        results = await service.find_similar_cases(
            visualization_id=query_viz_id,
            limit=10
        )
    
    # Empty results should still be a valid list
    assert isinstance(results, list)
    assert len(results) == 0
