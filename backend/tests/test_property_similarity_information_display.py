"""Property-based tests for similarity information display.

Feature: docwiz-surgical-platform, Property 19: Similarity information display

For any similar case view, the display should include both a numerical similarity
score and a text explanation of matching criteria.

Validates: Requirements 5.4
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.services.visualization_service import VisualizationService


# Custom strategies for test data
@st.composite
def similar_case_with_criteria_strategy(draw):
    """Generate a similar case with matching criteria."""
    viz_id = str(uuid.uuid4())
    procedure_type = draw(st.sampled_from(["facial", "body", "reconstructive"]))
    age_range = draw(st.sampled_from(["20-30", "30-40", "40-50", "50-60"]))
    outcome_rating = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return {
        "id": viz_id,
        "score": draw(st.floats(min_value=0.0, max_value=1.0)),
        "payload": {
            "visualization_id": viz_id,
            "procedure_type": procedure_type,
            "age_range": age_range,
            "outcome_rating": outcome_rating,
            "patient_id": f"patient_{draw(st.integers(min_value=1, max_value=1000))}",
            "created_at": "2024-01-01T00:00:00",
        }
    }


@pytest.mark.asyncio
@given(
    similar_results=st.lists(
        similar_case_with_criteria_strategy(),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100, deadline=None)
async def test_similarity_information_display(similar_results):
    """
    Feature: docwiz-surgical-platform, Property 19: Similarity information display
    
    For any similar case view, the display should include both a numerical similarity
    score and a text explanation of matching criteria.
    
    Validates: Requirements 5.4
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
    
    # Property: For any similar case view, the display should include:
    # 1. A numerical similarity score
    # 2. Text explanation of matching criteria (procedure_type, age_range, outcome_rating)
    
    for i, result in enumerate(results):
        # Check that similarity_score is present and is numeric
        assert "similarity_score" in result, "Result missing similarity_score"
        assert isinstance(result["similarity_score"], (int, float)), \
            "similarity_score is not numeric"
        assert 0.0 <= result["similarity_score"] <= 1.0, \
            "similarity_score out of range [0.0, 1.0]"
        
        # Check that matching criteria information is present
        # The criteria should include procedure_type, age_range, and outcome_rating
        assert "procedure_type" in result, "Result missing procedure_type (matching criterion)"
        assert isinstance(result["procedure_type"], str), "procedure_type is not a string"
        assert result["procedure_type"], "procedure_type is empty"
        
        assert "age_range" in result, "Result missing age_range (matching criterion)"
        assert isinstance(result["age_range"], str), "age_range is not a string"
        assert result["age_range"], "age_range is empty"
        
        assert "outcome_rating" in result, "Result missing outcome_rating (matching criterion)"
        assert isinstance(result["outcome_rating"], (int, float)), \
            "outcome_rating is not numeric"
        assert 0.0 <= result["outcome_rating"] <= 1.0, \
            "outcome_rating out of range [0.0, 1.0]"
        
        # Verify that the matching criteria match the original data
        original_result = similar_results[i]
        assert result["procedure_type"] == original_result["payload"]["procedure_type"], \
            "procedure_type doesn't match original data"
        assert result["age_range"] == original_result["payload"]["age_range"], \
            "age_range doesn't match original data"
        assert result["outcome_rating"] == original_result["payload"]["outcome_rating"], \
            "outcome_rating doesn't match original data"


@pytest.mark.asyncio
async def test_similarity_information_display_single_case():
    """Test that a single similar case has all required information."""
    service = VisualizationService()
    
    # Create a single test case
    viz_id = str(uuid.uuid4())
    similar_result = {
        "id": viz_id,
        "score": 0.95,
        "payload": {
            "visualization_id": viz_id,
            "procedure_type": "facial",
            "age_range": "30-40",
            "outcome_rating": 0.9,
            "patient_id": "patient_123",
            "created_at": "2024-01-01T00:00:00",
        }
    }
    
    # Mock the embedding service
    service.embedding_service.find_similar_cases = AsyncMock(return_value=[similar_result])
    
    # Mock get_visualization
    async def mock_get_viz(viz_id_param):
        if viz_id_param == viz_id:
            return {
                "id": viz_id,
                "patient_id": "patient_123",
                "procedure_id": "test_procedure",
                "procedure_name": "Test Procedure",
                "before_image_url": f"https://storage.example.com/before_{viz_id}.jpg",
                "after_image_url": f"https://storage.example.com/after_{viz_id}.jpg",
                "prompt_used": "test prompt",
                "generated_at": "2024-01-01T00:00:00",
                "confidence_score": 0.85,
                "metadata": {},
            }
        return {
            "id": "query_viz",
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
    
    service.get_visualization = mock_get_viz
    
    mock_image_data = b"fake_image_data"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_image_data
        
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        results = await service.find_similar_cases(
            visualization_id="query_viz",
            limit=10
        )
    
    assert len(results) == 1
    result = results[0]
    
    # Verify numerical similarity score
    assert result["similarity_score"] == 0.95
    
    # Verify matching criteria
    assert result["procedure_type"] == "facial"
    assert result["age_range"] == "30-40"
    assert result["outcome_rating"] == 0.9
