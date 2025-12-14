"""Property-based tests for embedding generation."""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from io import BytesIO
from PIL import Image
import numpy as np
from unittest.mock import AsyncMock

from app.services.embedding_service import EmbeddingService, EmbeddingGenerationError
from app.services.qdrant_client import QdrantClient


# Custom strategies for test data generation
@st.composite
def valid_image_data(draw):
    """Generate valid image data for testing."""
    # Use smaller, fixed dimensions to avoid Hypothesis buffer size limits
    width = draw(st.integers(min_value=100, max_value=200))
    height = draw(st.integers(min_value=100, max_value=200))
    
    # Generate random RGB image using numpy directly
    img_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    
    # Create PIL Image
    image = Image.fromarray(img_array, mode='RGB')
    
    # Convert to bytes
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


def create_embedding_service():
    """Create embedding service with mocked Qdrant client."""
    # Create a mock Qdrant client
    mock_qdrant = AsyncMock(spec=QdrantClient)
    mock_qdrant.upsert_embedding = AsyncMock()
    mock_qdrant.search_similar = AsyncMock(return_value=[])
    service = EmbeddingService(qdrant_client=mock_qdrant)
    return service


@given(image_data=valid_image_data())
@settings(
    max_examples=100,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_property_16_embedding_generation(image_data):
    """
    Feature: docwiz-surgical-platform, Property 16: Embedding generation
    
    Validates: Requirements 5.1
    
    For any uploaded image, the system should generate a vector embedding
    and store it in Qdrant with a valid embedding ID.
    
    This test verifies that:
    1. Embeddings are generated for all valid images
    2. Embeddings have the correct size (768)
    3. Embeddings are normalized (unit length or close to it)
    4. Embeddings contain valid float values (no NaN or Inf)
    """
    embedding_service = create_embedding_service()
    
    # Generate embedding
    embedding = await embedding_service.generate_embedding(image_data)
    
    # Property 1: Embedding should be generated (not None or empty)
    assert embedding is not None
    assert len(embedding) > 0
    
    # Property 2: Embedding should have the correct size
    assert len(embedding) == 768, f"Expected embedding size 768, got {len(embedding)}"
    
    # Property 3: All values should be valid floats (no NaN or Inf)
    for i, value in enumerate(embedding):
        assert isinstance(value, float), f"Value at index {i} is not a float: {type(value)}"
        assert not np.isnan(value), f"Value at index {i} is NaN"
        assert not np.isinf(value), f"Value at index {i} is Inf"
    
    # Property 4: Embedding should be normalized (approximately unit length)
    # Allow some tolerance for floating point arithmetic
    embedding_array = np.array(embedding)
    norm = np.linalg.norm(embedding_array)
    assert 0.9 <= norm <= 1.1, f"Embedding norm {norm} is not close to 1.0"


@given(
    image_data=valid_image_data(),
    metadata=visualization_metadata()
)
@settings(
    max_examples=50,
    deadline=10000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_embedding_storage_generates_valid_id(image_data, metadata):
    """
    Test that storing an embedding generates a valid point ID.
    
    This verifies that the storage operation:
    1. Generates a consistent point ID from visualization ID
    2. Returns a non-empty string ID
    """
    embedding_service = create_embedding_service()
    
    # Store embedding
    point_id = await embedding_service.store_embedding(
        image_data=image_data,
        visualization_id=metadata["visualization_id"],
        procedure_type=metadata["procedure_type"],
        age_range=metadata["age_range"],
        outcome_rating=metadata["outcome_rating"],
        patient_id=metadata["patient_id"],
    )
    
    # Verify point ID is valid
    assert point_id is not None
    assert isinstance(point_id, str)
    assert len(point_id) > 0
    
    # Verify upsert was called
    assert embedding_service.qdrant_client.upsert_embedding.called


@given(
    image_data1=valid_image_data(),
    image_data2=valid_image_data()
)
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_embedding_consistency(image_data1, image_data2):
    """
    Test that the same image produces the same embedding.
    
    This verifies deterministic behavior of the embedding generation.
    """
    embedding_service = create_embedding_service()
    
    # Generate embedding twice for the same image
    embedding1_a = await embedding_service.generate_embedding(image_data1)
    embedding1_b = await embedding_service.generate_embedding(image_data1)
    
    # Same image should produce identical embeddings
    assert len(embedding1_a) == len(embedding1_b)
    for i in range(len(embedding1_a)):
        assert abs(embedding1_a[i] - embedding1_b[i]) < 1e-6, \
            f"Embeddings differ at index {i}: {embedding1_a[i]} vs {embedding1_b[i]}"
    
    # Different images should produce different embeddings
    # Only test if the images are actually different
    if image_data1 != image_data2:
        embedding2 = await embedding_service.generate_embedding(image_data2)
        
        # Calculate similarity (dot product of normalized vectors)
        similarity = sum(a * b for a, b in zip(embedding1_a, embedding2))
        
        # Different images should not be completely identical (similarity < 1.0)
        # Note: Simple feature extraction may produce similar embeddings for minimal images
        # In production, use a pre-trained model like CLIP for better discrimination
        assert similarity < 1.0, f"Different images produced identical embeddings: {similarity}"


@given(binary_data=st.binary(min_size=0, max_size=100))
@settings(
    max_examples=50,
    deadline=2000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_invalid_image_data_handling(binary_data):
    """
    Test that invalid image data is handled gracefully.
    
    This verifies error handling for corrupted or invalid image data.
    """
    embedding_service = create_embedding_service()
    
    # Assume the data is actually invalid (not a valid image)
    assume(len(binary_data) < 1000)  # Too small to be a valid image
    
    # Should raise an error for invalid image data
    with pytest.raises(EmbeddingGenerationError):
        await embedding_service.generate_embedding(binary_data)
