"""Property-based tests for Qdrant vector operations."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from io import BytesIO
from PIL import Image
import numpy as np
from unittest.mock import AsyncMock, MagicMock
from typing import List

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
def visualization_metadata(draw):
    """Generate visualization metadata for testing."""
    procedure_types = [
        "rhinoplasty",
        "breast_augmentation",
        "facelift",
        "liposuction",
        "cleft_lip_repair"
    ]
    
    age_ranges = ["20-30", "30-40", "40-50", "50-60", "60-70"]
    
    return {
        "visualization_id": draw(st.uuids()).hex,
        "procedure_type": draw(st.sampled_from(procedure_types)),
        "age_range": draw(st.sampled_from(age_ranges)),
        "outcome_rating": draw(st.floats(min_value=0.0, max_value=1.0)),
        "patient_id": draw(st.uuids()).hex,
    }


def create_embedding_service_with_tracking():
    """Create embedding service that tracks Qdrant operations."""
    mock_qdrant = AsyncMock(spec=QdrantClient)
    
    # Track calls
    mock_qdrant.upsert_calls = []
    mock_qdrant.search_calls = []
    
    async def track_upsert(point_id, embedding, metadata):
        mock_qdrant.upsert_calls.append({
            "point_id": point_id,
            "embedding": embedding,
            "metadata": metadata
        })
    
    async def track_search(query_embedding, limit, procedure_type=None, age_range=None, min_outcome_rating=None):
        mock_qdrant.search_calls.append({
            "query_embedding": query_embedding,
            "limit": limit,
            "procedure_type": procedure_type,
            "age_range": age_range,
            "min_outcome_rating": min_outcome_rating
        })
        return []
    
    mock_qdrant.upsert_embedding = track_upsert
    mock_qdrant.search_similar = track_search
    
    service = EmbeddingService(qdrant_client=mock_qdrant)
    return service, mock_qdrant


@given(
    image_data=valid_image_data(),
    metadata=visualization_metadata()
)
@settings(
    max_examples=100,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_property_29_qdrant_vector_operations(image_data, metadata):
    """
    Feature: docwiz-surgical-platform, Property 29: Qdrant vector operations
    
    Validates: Requirements 9.4
    
    For any embedding storage or similarity search operation, the system
    should use Qdrant client for vector database interactions.
    
    This test verifies that:
    1. Embedding storage operations call Qdrant upsert
    2. Similarity search operations call Qdrant search
    3. Vector embeddings passed to Qdrant have correct dimensions
    4. Metadata is properly passed to Qdrant operations
    5. Qdrant client is used for all vector database interactions
    """
    embedding_service, mock_qdrant = create_embedding_service_with_tracking()
    
    # Test 1: Storage operation uses Qdrant
    point_id = await embedding_service.store_embedding(
        image_data=image_data,
        visualization_id=metadata["visualization_id"],
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        outcome_rating=metadata["outcome_rating"],
        patient_id=metadata["patient_id"],
    )
    
    # Property 1: Qdrant upsert should be called
    assert len(mock_qdrant.upsert_calls) == 1, \
        "Qdrant upsert should be called exactly once for storage"
    
    upsert_call = mock_qdrant.upsert_calls[0]
    
    # Property 2: Point ID should be valid
    assert upsert_call["point_id"] is not None
    assert len(upsert_call["point_id"]) > 0
    
    # Property 3: Embedding should have correct dimensions (768)
    assert len(upsert_call["embedding"]) == 768, \
        f"Embedding should have 768 dimensions, got {len(upsert_call['embedding'])}"
    
    # Property 4: Metadata should be properly passed
    stored_metadata = upsert_call["metadata"]
    assert stored_metadata["visualization_id"] == metadata["visualization_id"]
    assert stored_metadata["procedure_type"] == metadata["procedure_type"]
    assert stored_metadata["age_range"] == metadata["age_range"]
    assert stored_metadata["outcome_rating"] == metadata["outcome_rating"]
    assert stored_metadata["patient_id"] == metadata["patient_id"]
    assert "created_at" in stored_metadata
    
    # Test 2: Search operation uses Qdrant
    await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        min_outcome_rating=metadata["outcome_rating"],
        limit=10,
    )
    
    # Property 5: Qdrant search should be called
    assert len(mock_qdrant.search_calls) == 1, \
        "Qdrant search should be called exactly once for similarity search"
    
    search_call = mock_qdrant.search_calls[0]
    
    # Property 6: Query embedding should have correct dimensions
    assert len(search_call["query_embedding"]) == 768, \
        f"Query embedding should have 768 dimensions, got {len(search_call['query_embedding'])}"
    
    # Property 7: Search filters should be passed correctly
    assert search_call["procedure_type"] == metadata["procedure_type"]
    assert search_call["age_range"] == metadata["age_range"]
    assert search_call["min_outcome_rating"] == metadata["outcome_rating"]
    assert search_call["limit"] == 10


@given(
    image_data=valid_image_data(),
    metadata=visualization_metadata()
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_qdrant_used_for_all_vector_operations(image_data, metadata):
    """
    Test that Qdrant client is used for ALL vector database operations.
    
    No vector operations should bypass the Qdrant client.
    """
    embedding_service, mock_qdrant = create_embedding_service_with_tracking()
    
    # Perform multiple operations
    await embedding_service.store_embedding(
        image_data=image_data,
        visualization_id=metadata["visualization_id"],
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        outcome_rating=metadata["outcome_rating"],
        patient_id=metadata["patient_id"],
    )
    
    await embedding_service.find_similar_cases(
        image_data=image_data,
        limit=5,
    )
    
    # All operations should go through Qdrant client
    assert len(mock_qdrant.upsert_calls) == 1, "Storage should use Qdrant"
    assert len(mock_qdrant.search_calls) == 1, "Search should use Qdrant"


@given(
    image_data=valid_image_data(),
    metadata=visualization_metadata(),
    num_searches=st.integers(min_value=1, max_value=5)
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_multiple_qdrant_operations(image_data, metadata, num_searches):
    """
    Test that multiple Qdrant operations are tracked correctly.
    
    Each operation should result in a corresponding Qdrant call.
    """
    embedding_service, mock_qdrant = create_embedding_service_with_tracking()
    
    # Store embedding
    await embedding_service.store_embedding(
        image_data=image_data,
        visualization_id=metadata["visualization_id"],
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        outcome_rating=metadata["outcome_rating"],
        patient_id=metadata["patient_id"],
    )
    
    # Perform multiple searches
    for _ in range(num_searches):
        await embedding_service.find_similar_cases(
            image_data=image_data,
            limit=10,
        )
    
    # Verify correct number of operations
    assert len(mock_qdrant.upsert_calls) == 1
    assert len(mock_qdrant.search_calls) == num_searches


@given(
    image_data=valid_image_data(),
    metadata=visualization_metadata()
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_qdrant_receives_valid_vector_data(image_data, metadata):
    """
    Test that all vectors passed to Qdrant are valid.
    
    Vectors should be:
    - Correct size (768)
    - Contain only valid floats (no NaN or Inf)
    - Be normalized (approximately unit length)
    """
    embedding_service, mock_qdrant = create_embedding_service_with_tracking()
    
    await embedding_service.store_embedding(
        image_data=image_data,
        visualization_id=metadata["visualization_id"],
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        outcome_rating=metadata["outcome_rating"],
        patient_id=metadata["patient_id"],
    )
    
    await embedding_service.find_similar_cases(
        image_data=image_data,
        limit=10,
    )
    
    # Check storage vector
    storage_vector = mock_qdrant.upsert_calls[0]["embedding"]
    assert len(storage_vector) == 768
    for value in storage_vector:
        assert isinstance(value, float)
        assert not np.isnan(value)
        assert not np.isinf(value)
    
    # Check vector is normalized
    norm = np.linalg.norm(storage_vector)
    assert 0.9 <= norm <= 1.1
    
    # Check search vector
    search_vector = mock_qdrant.search_calls[0]["query_embedding"]
    assert len(search_vector) == 768
    for value in search_vector:
        assert isinstance(value, float)
        assert not np.isnan(value)
        assert not np.isinf(value)
    
    # Check vector is normalized
    norm = np.linalg.norm(search_vector)
    assert 0.9 <= norm <= 1.1


@given(
    image_data=valid_image_data(),
    metadata=visualization_metadata(),
    limit=st.integers(min_value=1, max_value=100)
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_qdrant_search_parameters_passed_correctly(image_data, metadata, limit):
    """
    Test that all search parameters are correctly passed to Qdrant.
    
    This ensures no parameters are lost or modified in transit.
    """
    embedding_service, mock_qdrant = create_embedding_service_with_tracking()
    
    await embedding_service.find_similar_cases(
        image_data=image_data,
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        min_outcome_rating=metadata["outcome_rating"],
        limit=limit,
    )
    
    search_call = mock_qdrant.search_calls[0]
    
    # All parameters should match exactly
    assert search_call["procedure_type"] == metadata["procedure_type"]
    assert search_call["age_range"] == metadata["age_range"]
    assert search_call["min_outcome_rating"] == metadata["outcome_rating"]
    assert search_call["limit"] == limit
