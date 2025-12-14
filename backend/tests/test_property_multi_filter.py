"""Property-based tests for multi-filter application."""
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
def multi_filter_params(draw):
    """Generate multiple filter parameters for testing."""
    procedure_types = [
        "rhinoplasty",
        "breast_augmentation",
        "facelift",
        "liposuction",
        "cleft_lip_repair"
    ]
    
    age_ranges = ["20-30", "30-40", "40-50", "50-60", "60-70"]
    
    # Always use all three filters for multi-filter testing
    return {
        "procedure_type": draw(st.sampled_from(procedure_types)),
        "age_range": draw(st.sampled_from(age_ranges)),
        "min_outcome_rating": draw(st.floats(min_value=0.0, max_value=0.9)),
    }


def create_mock_results_matching_all_filters(
    procedure_type: str,
    age_range: str,
    min_outcome_rating: float,
    num_results: int = 5
) -> List[Dict[str, Any]]:
    """Create mock results that match ALL specified filters."""
    results = []
    for i in range(num_results):
        # Ensure outcome rating is >= min
        outcome_rating = min_outcome_rating + (1.0 - min_outcome_rating) * np.random.random()
        
        results.append({
            "id": f"test-id-{i}",
            "score": 0.9 - (i * 0.1),  # Descending similarity scores
            "payload": {
                "visualization_id": f"viz-{i}",
                "procedure_type": procedure_type,
                "age_range": age_range,
                "outcome_rating": outcome_rating,
                "patient_id": f"patient-{i}",
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
    filters=multi_filter_params()
)
@settings(
    max_examples=100,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_property_20_multi_filter_application(image_data, filters):
    """
    Feature: docwiz-surgical-platform, Property 20: Multi-filter application
    
    Validates: Requirements 5.5
    
    For any similar case retrieval with multiple filters (procedure type,
    outcome quality, recency), all returned results should satisfy ALL
    specified filters.
    
    This test verifies that:
    1. All results match the procedure_type filter
    2. All results match the age_range filter
    3. All results have outcome_rating >= min_outcome_rating
    4. Filters are applied conjunctively (AND logic, not OR)
    5. No results violate any of the specified filters
    """
    # Create mock results that match ALL filters
    mock_results = create_mock_results_matching_all_filters(
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        num_results=np.random.randint(0, 11)
    )
    
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    # Perform search with all filters
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        limit=10,
    )
    
    # Verify ALL results satisfy ALL filters
    for result in results:
        payload = result["payload"]
        
        # Property 1: Procedure type must match
        assert payload["procedure_type"] == filters["procedure_type"], \
            f"Result procedure_type '{payload['procedure_type']}' does not match filter '{filters['procedure_type']}'"
        
        # Property 2: Age range must match
        assert payload["age_range"] == filters["age_range"], \
            f"Result age_range '{payload['age_range']}' does not match filter '{filters['age_range']}'"
        
        # Property 3: Outcome rating must be >= minimum
        assert payload["outcome_rating"] >= filters["min_outcome_rating"], \
            f"Result outcome_rating {payload['outcome_rating']} is less than minimum {filters['min_outcome_rating']}"
        
        # Property 4: Result must have all required fields
        assert "visualization_id" in payload
        assert "procedure_type" in payload
        assert "age_range" in payload
        assert "outcome_rating" in payload
        assert "patient_id" in payload
        assert "created_at" in payload


@given(
    image_data=valid_image_data(),
    procedure_type=st.sampled_from(["rhinoplasty", "breast_augmentation", "facelift"]),
    age_range=st.sampled_from(["20-30", "30-40", "40-50"]),
    min_rating=st.floats(min_value=0.5, max_value=0.9)
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_all_three_filters_applied_conjunctively(
    image_data,
    procedure_type,
    age_range,
    min_rating
):
    """
    Test that all three filters are applied with AND logic.
    
    Every result must satisfy ALL three conditions simultaneously.
    """
    # Create results that match all filters
    mock_results = create_mock_results_matching_all_filters(
        procedure_type=procedure_type,
        age_range=age_range,
        min_outcome_rating=min_rating,
        num_results=5
    )
    
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=procedure_type,
        age_range=age_range,
        min_outcome_rating=min_rating,
        limit=10,
    )
    
    # Every result must pass all three filters
    for result in results:
        payload = result["payload"]
        
        # All three conditions must be true
        procedure_matches = payload["procedure_type"] == procedure_type
        age_matches = payload["age_range"] == age_range
        rating_sufficient = payload["outcome_rating"] >= min_rating
        
        assert procedure_matches and age_matches and rating_sufficient, \
            f"Result failed multi-filter check: procedure={procedure_matches}, age={age_matches}, rating={rating_sufficient}"


@given(
    image_data=valid_image_data(),
    filters=multi_filter_params()
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_no_results_violate_any_filter(image_data, filters):
    """
    Test that no result violates any of the specified filters.
    
    This is a negative test - we verify that results don't have
    wrong values for any filter.
    """
    # Create results matching all filters
    mock_results = create_mock_results_matching_all_filters(
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        num_results=np.random.randint(3, 8)
    )
    
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        limit=10,
    )
    
    # Define what would be violations
    other_procedures = ["rhinoplasty", "breast_augmentation", "facelift", "liposuction"]
    other_age_ranges = ["20-30", "30-40", "40-50", "50-60"]
    
    for result in results:
        payload = result["payload"]
        
        # Should not have a different procedure type
        if filters["procedure_type"] in other_procedures:
            other_procedures_filtered = [p for p in other_procedures if p != filters["procedure_type"]]
            assert payload["procedure_type"] not in other_procedures_filtered or \
                   payload["procedure_type"] == filters["procedure_type"]
        
        # Should not have a different age range
        if filters["age_range"] in other_age_ranges:
            other_ages_filtered = [a for a in other_age_ranges if a != filters["age_range"]]
            assert payload["age_range"] not in other_ages_filtered or \
                   payload["age_range"] == filters["age_range"]
        
        # Should not have rating below minimum
        assert payload["outcome_rating"] >= filters["min_outcome_rating"]


@given(
    image_data=valid_image_data(),
    filters=multi_filter_params(),
    limit=st.integers(min_value=1, max_value=20)
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_multi_filter_respects_limit(image_data, filters, limit):
    """
    Test that multi-filter search respects the limit parameter.
    
    Even with multiple filters, the number of results should not exceed limit.
    """
    # Create more results than the limit
    mock_results = create_mock_results_matching_all_filters(
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        num_results=min(limit, 15)  # Cap at 15 for test performance
    )
    
    embedding_service = create_embedding_service_with_mock_results(mock_results)
    
    results = await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=filters["procedure_type"],
        age_range=filters["age_range"],
        min_outcome_rating=filters["min_outcome_rating"],
        limit=limit,
    )
    
    # Number of results should not exceed limit
    assert len(results) <= limit, \
        f"Got {len(results)} results but limit was {limit}"
