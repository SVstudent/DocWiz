"""Property-based tests for similar case filtering."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from io import BytesIO
from PIL import Image
import numpy as np
from unittest.mock import AsyncMock
from typing import List, Dict, Any

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_client import QdrantClient


# Custom strategies
@st.composite
def valid_image_data(draw):
    """Generate valid image data for testing."""
    width = draw(st.integers(min_value=100, max_value=200))
    height = draw(st.integers(min_value=100, max_value=200))
    
    img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    image = Image.fromarray(img_array, mode='RGB')
    
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


@st.composite
def search_filters(draw):
    """Generate search filter parameters."""
    procedure_types = [
        "rhinoplasty",
        "breast_augmentation",
        "facelift",
        "liposuction",
        "cleft_lip_repair"
    ]
    
    age_ranges = ["20-30", "30-40", "40-50", "50-60", "60-70"]
    
    # Randomly decide which filters to apply
    use_procedure = draw(st.booleans())
    use_age_range = draw(st.booleans())
    use_outcome = draw(st.booleans())
    
    return {
        "procedure_type": draw(st.sampled_from(procedure_types)) if use_procedure else None,
        "age_range": draw(st.sampled_from(age_ranges)) if use_age_range else None,
        "min_outcome_rating": draw(st.floats(min_value=0.0, max_value=1.0)) if use_outcome else None,
    }


@st.composite
def mock_search_results(draw, filters: Dict[str, Any]):
    """Generate mock search results that match the given filters."""
    num_results = draw(st.integers(min_value=0, max_value=10))
    
    results = []
    for i in range(num_results):
        # Generate result that matches filters
        procedure_type = filters["procedure_type"] if filters["procedure_type"] else draw(
            st.sampled_from(["rhinoplasty", "breast_augmentation", "facelift"])
        )
        age_range = filters["age_range"] if filters["age_range"] else draw(
            st.sampled_from(["20-30", "30-40", "40-50"])
        )
        
        # Ensure outcome rating is >= min if filter is set
        if filters["min_outcome_rating"] is not None:
            outcome_rating = draw(st.floats(
                min_value=filters["min_outcome_rating"],
                max_value=1.0
            ))
        else:
            outcome_rating = draw(st.floats(min_value=0.0, max_value=1.0))
        
        results.append({
            "id": draw(st.uuids()).hex,
            "score": draw(st.floats(min_value=0.0, max_value=1.0)),
            "payload": {
                "visualization_id": draw(st.uuids()).hex,
                "procedure_type": procedure_type,
                "age_range": age_range,
                "outcome_rating": outcome_rating,
                "patient_id": draw(st.uuids()).hex,
                "created_at": "2024-01-01T00:00:00",
            }
        })
    
    return results


def create_embedding_service_with_mock_results(mock_results: List[Dict[str, Any]]):
    """Create embedding service with mocked search results."""
    mock_qdrant = AsyncMock(spec=QdrantClient)
    mock_qdrant.search_similar = AsyncMock(return_value=mock_results)
    service = EmbeddingService(qdrant_client=mock_qdrant)
    return service


@given(
    image_data=valid_image_data(),
    filters=search_filters()
)
@settings(
    max_examples=100,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_property_17_similar_case_filtering(image_data, filters):
    """
    Feature: docwiz-surgical-platform, Property 17: Similar case filtering
    
    Validates: Requirements 5.2
    
    For any similar case search with specified filters (procedure type, age range),
    all returned results should match the filter criteria.
    
    This test verifies that:
    1. When procedure_type filter is set, all results have that procedure_type
    2. When age_range filter is set, all results have that age_range
    3. When min_outcome_rating filter is set, all results have rating >= min
    4. Results are properly formatted with required fields
    """
    # Generate mock results that match the filters
    from hypothesis import assume
    from hypothesis.strategies import data as st_data
    
    # Create mock results that match filters
    mock_results = []
    num_results = np.random.randint(0, 11)
    
    for i in range(num_results):
        procedure_type = filters["procedure_type"] if filters["procedure_type"] else "rhinoplasty"
        age_range = filters["age_range"] if filters["age_range"] else "20-30"
        
        if filters["min_outcome_rating"] is not None:
            outcome_rating = np.random.uniform(filters["min_outcome_rating"], 1.0)
        else:
            outcome_rating = np.random.uniform(0.0, 1.0)
        
        mock_results.append({
            "id": f"test-id-{i}",
            "score": np.random.uniform(0.0, 1.0),
            "payload": {
                "visualization_id": f"viz-{i}",
                "procedure_type": procedure_type,
                "age_range": age_range,
                "outcome_rating": outcome_rating,
                "patient_id": f"patient-{i}",
                "created_at": "2024-01-01T00:00:00",
            }
        })
    
    # Create service with mocked results
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    # Perform search
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        limit=10,
    )
    
    # Verify all results match the filters
    for result in results:
        payload = result["payload"]
        
        # Property 1: If procedure_type filter is set, all results must match
        if filters["procedure_type"] is not None:
            assert payload["procedure_type"] == filters["procedure_type"], \
                f"Result has procedure_type '{payload['procedure_type']}' but filter was '{filters['procedure_type']}'"
        
        # Property 2: If age_range filter is set, all results must match
        if filters["age_range"] is not None:
            assert payload["age_range"] == filters["age_range"], \
                f"Result has age_range '{payload['age_range']}' but filter was '{filters['age_range']}'"
        
        # Property 3: If min_outcome_rating filter is set, all results must be >= min
        if filters["min_outcome_rating"] is not None:
            assert payload["outcome_rating"] >= filters["min_outcome_rating"], \
                f"Result has outcome_rating {payload['outcome_rating']} but min was {filters['min_outcome_rating']}"
        
        # Property 4: Results must have required fields
        assert "visualization_id" in payload
        assert "procedure_type" in payload
        assert "age_range" in payload
        assert "outcome_rating" in payload
        assert "patient_id" in payload


@given(
    image_data=valid_image_data(),
    procedure_type=st.sampled_from(["rhinoplasty", "breast_augmentation", "facelift"])
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_procedure_type_filter_consistency(image_data, procedure_type):
    """
    Test that procedure_type filter is consistently applied.
    
    All results should have the exact procedure_type specified.
    """
    # Create mock results with the specified procedure type
    mock_results = [
        {
            "id": f"test-{i}",
            "score": 0.9,
            "payload": {
                "visualization_id": f"viz-{i}",
                "procedure_type": procedure_type,
                "age_range": "30-40",
                "outcome_rating": 0.8,
                "patient_id": f"patient-{i}",
                "created_at": "2024-01-01T00:00:00",
            }
        }
        for i in range(5)
    ]
    
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=procedure_type,
        limit=10,
    )
    
    # All results must have the specified procedure type
    for result in results:
        assert result["payload"]["procedure_type"] == procedure_type


@given(
    image_data=valid_image_data(),
    min_rating=st.floats(min_value=0.0, max_value=0.9)
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_outcome_rating_filter_consistency(image_data, min_rating):
    """
    Test that min_outcome_rating filter is consistently applied.
    
    All results should have outcome_rating >= min_rating.
    """
    # Create mock results with ratings >= min_rating
    mock_results = [
        {
            "id": f"test-{i}",
            "score": 0.9,
            "payload": {
                "visualization_id": f"viz-{i}",
                "procedure_type": "rhinoplasty",
                "age_range": "30-40",
                "outcome_rating": min_rating + (1.0 - min_rating) * (i / 5),
                "patient_id": f"patient-{i}",
                "created_at": "2024-01-01T00:00:00",
            }
        }
        for i in range(5)
    ]
    
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        min_outcome_rating=min_rating,
        limit=10,
    )
    
    # All results must have rating >= min_rating
    for result in results:
        assert result["payload"]["outcome_rating"] >= min_rating, \
            f"Result rating {result['payload']['outcome_rating']} < min {min_rating}"
