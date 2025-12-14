"""Property-based tests for comparison source consistency."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import uuid

from app.services.comparison_service import ComparisonService, ComparisonError
from app.services.visualization_service import VisualizationService
from app.services.procedure_service import ProcedureService


# Custom strategies for test data generation
@st.composite
def procedure_id_list(draw, min_size=2, max_size=5):
    """Generate a list of procedure IDs."""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    procedure_ids = [
        "rhinoplasty-001",
        "breast-augmentation-001",
        "facelift-001",
        "liposuction-001",
        "cleft-lip-repair-001",
        "brow-lift-001",
        "chin-augmentation-001",
    ]
    return draw(st.lists(
        st.sampled_from(procedure_ids),
        min_size=size,
        max_size=size,
        unique=True
    ))


@st.composite
def comparison_test_data(draw):
    """Generate test data for comparison creation."""
    return {
        "source_image_id": draw(st.uuids()).hex,
        "procedure_ids": draw(procedure_id_list()),
        "patient_id": draw(st.one_of(st.none(), st.uuids().map(lambda x: x.hex))),
    }


def create_mock_procedure(procedure_id: str) -> dict:
    """Create a mock procedure dictionary."""
    procedure_names = {
        "rhinoplasty-001": "Rhinoplasty",
        "breast-augmentation-001": "Breast Augmentation",
        "facelift-001": "Facelift",
        "liposuction-001": "Liposuction",
        "cleft-lip-repair-001": "Cleft Lip Repair",
        "brow-lift-001": "Brow Lift",
        "chin-augmentation-001": "Chin Augmentation",
    }
    
    return {
        "id": procedure_id,
        "name": procedure_names.get(procedure_id, "Unknown Procedure"),
        "category": "facial",
        "description": f"Description for {procedure_id}",
        "typical_cost_range": [5000, 15000],
        "recovery_days": 14,
        "risk_level": "medium",
        "cpt_codes": ["12345"],
        "icd10_codes": ["Z00.00"],
        "prompt_template": "Generate surgical preview",
    }


def create_mock_visualization(
    viz_id: str,
    source_image_id: str,
    procedure_id: str,
    procedure_name: str
) -> dict:
    """Create a mock visualization result."""
    return {
        "id": viz_id,
        "patient_id": None,
        "procedure_id": procedure_id,
        "procedure_name": procedure_name,
        "before_image_url": f"https://storage.example.com/images/{source_image_id}",
        "after_image_url": f"https://storage.example.com/images/{viz_id}",
        "prompt_used": "Generate surgical preview",
        "generated_at": datetime.utcnow(),
        "confidence_score": 0.85,
        "metadata": {},
    }


def create_comparison_service_with_mocks():
    """Create comparison service with mocked dependencies."""
    # Mock visualization service
    mock_viz_service = AsyncMock(spec=VisualizationService)
    
    # Mock procedure service
    mock_proc_service = AsyncMock(spec=ProcedureService)
    
    # Create comparison service
    service = ComparisonService(
        visualization_service=mock_viz_service,
        procedure_service=mock_proc_service,
    )
    
    return service, mock_viz_service, mock_proc_service


@given(test_data=comparison_test_data())
@settings(
    max_examples=100,
    deadline=10000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_property_13_comparison_source_consistency(test_data):
    """
    Feature: docwiz-surgical-platform, Property 13: Comparison source consistency
    
    Validates: Requirements 4.1
    
    For any multi-procedure comparison, all generated visualizations should
    reference the same source image identifier.
    
    This test verifies that:
    1. All visualizations in a comparison use the same source_image_id
    2. The comparison result stores the source_image_id
    3. Each procedure's before_image_url references the same source image
    """
    service, mock_viz_service, mock_proc_service = create_comparison_service_with_mocks()
    
    source_image_id = test_data["source_image_id"]
    procedure_ids = test_data["procedure_ids"]
    patient_id = test_data["patient_id"]
    
    # Setup mocks
    # Mock procedure service to return valid procedures
    async def mock_get_procedure(proc_id):
        proc_dict = create_mock_procedure(proc_id)
        # Create a mock Pydantic model
        mock_model = MagicMock()
        mock_model.model_dump.return_value = proc_dict
        return mock_model
    
    mock_proc_service.get_procedure_by_id.side_effect = mock_get_procedure
    
    # Mock visualization service to return visualizations
    visualization_counter = [0]
    
    async def mock_generate_preview(image_id, procedure_id, patient_id=None):
        viz_id = str(uuid.uuid4())
        procedure = create_mock_procedure(procedure_id)
        visualization_counter[0] += 1
        return create_mock_visualization(
            viz_id,
            image_id,
            procedure_id,
            procedure["name"]
        )
    
    mock_viz_service.generate_surgical_preview.side_effect = mock_generate_preview
    
    # Mock Firestore
    from unittest.mock import patch
    with patch('app.services.comparison_service.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_document = MagicMock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.set.return_value = None
        
        mock_get_db.return_value = mock_db
        
        # Create comparison
        comparison = await service.create_comparison(
            source_image_id=source_image_id,
            procedure_ids=procedure_ids,
            patient_id=patient_id,
        )
        
        # Property 1: Comparison should store the source_image_id
        assert "source_image_id" in comparison
        assert comparison["source_image_id"] == source_image_id
        
        # Property 2: All procedures should be present
        assert "procedures" in comparison
        assert len(comparison["procedures"]) == len(procedure_ids)
        
        # Property 3: All visualizations should use the same source image
        for proc_data in comparison["procedures"]:
            # Check that before_image_url references the source image
            assert source_image_id in proc_data["before_image_url"], \
                f"Procedure {proc_data['procedure_name']} before_image_url does not reference source image"
        
        # Property 4: Verify all visualizations were generated with the same source_image_id
        for call in mock_viz_service.generate_surgical_preview.call_args_list:
            args, kwargs = call
            # Check positional args
            if len(args) > 0:
                assert args[0] == source_image_id, \
                    f"Visualization generated with wrong source image: {args[0]} != {source_image_id}"
            # Check keyword args
            if "image_id" in kwargs:
                assert kwargs["image_id"] == source_image_id, \
                    f"Visualization generated with wrong source image: {kwargs['image_id']} != {source_image_id}"


@given(
    source_image_id=st.uuids().map(lambda x: x.hex),
    procedure_ids=procedure_id_list(min_size=2, max_size=4)
)
@settings(
    max_examples=50,
    deadline=10000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_comparison_source_image_consistency_in_urls(source_image_id, procedure_ids):
    """
    Test that all before_image_urls in a comparison reference the same source image.
    
    This is a more focused test on the URL consistency aspect.
    """
    service, mock_viz_service, mock_proc_service = create_comparison_service_with_mocks()
    
    # Setup mocks
    async def mock_get_procedure(proc_id):
        proc_dict = create_mock_procedure(proc_id)
        mock_model = MagicMock()
        mock_model.model_dump.return_value = proc_dict
        return mock_model
    
    mock_proc_service.get_procedure_by_id.side_effect = mock_get_procedure
    
    async def mock_generate_preview(image_id, procedure_id, patient_id=None):
        viz_id = str(uuid.uuid4())
        procedure = create_mock_procedure(procedure_id)
        return create_mock_visualization(
            viz_id,
            image_id,
            procedure_id,
            procedure["name"]
        )
    
    mock_viz_service.generate_surgical_preview.side_effect = mock_generate_preview
    
    # Mock Firestore
    from unittest.mock import patch
    with patch('app.services.comparison_service.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_document = MagicMock()
        
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.set.return_value = None
        
        mock_get_db.return_value = mock_db
        
        # Create comparison
        comparison = await service.create_comparison(
            source_image_id=source_image_id,
            procedure_ids=procedure_ids,
            patient_id=None,
        )
        
        # Extract all before_image_urls
        before_urls = [proc["before_image_url"] for proc in comparison["procedures"]]
        
        # All URLs should be identical (same source image)
        assert len(set(before_urls)) == 1, \
            f"Before image URLs are not consistent: {before_urls}"
        
        # The URL should contain the source_image_id
        assert source_image_id in before_urls[0], \
            f"Before image URL does not contain source_image_id: {before_urls[0]}"


@given(procedure_ids=st.lists(st.text(min_size=1), min_size=0, max_size=1))
@settings(
    max_examples=50,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_comparison_requires_minimum_procedures(procedure_ids):
    """
    Test that comparison creation fails with fewer than 2 procedures.
    
    This verifies the minimum requirement for comparisons.
    """
    service, _, _ = create_comparison_service_with_mocks()
    
    source_image_id = str(uuid.uuid4())
    
    # Should raise ComparisonError for < 2 procedures
    with pytest.raises(ComparisonError, match="At least 2 procedures required"):
        await service.create_comparison(
            source_image_id=source_image_id,
            procedure_ids=procedure_ids,
            patient_id=None,
        )
