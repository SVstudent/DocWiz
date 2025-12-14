"""Property-based tests for comparison data completeness."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import uuid

from app.services.comparison_service import ComparisonService
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
    """Create a mock procedure dictionary with varying data."""
    procedure_data = {
        "rhinoplasty-001": {
            "name": "Rhinoplasty",
            "typical_cost_range": [5000, 15000],
            "recovery_days": 14,
            "risk_level": "medium",
        },
        "breast-augmentation-001": {
            "name": "Breast Augmentation",
            "typical_cost_range": [8000, 20000],
            "recovery_days": 21,
            "risk_level": "medium",
        },
        "facelift-001": {
            "name": "Facelift",
            "typical_cost_range": [10000, 30000],
            "recovery_days": 28,
            "risk_level": "high",
        },
        "liposuction-001": {
            "name": "Liposuction",
            "typical_cost_range": [3000, 10000],
            "recovery_days": 7,
            "risk_level": "low",
        },
        "cleft-lip-repair-001": {
            "name": "Cleft Lip Repair",
            "typical_cost_range": [7000, 18000],
            "recovery_days": 14,
            "risk_level": "medium",
        },
        "brow-lift-001": {
            "name": "Brow Lift",
            "typical_cost_range": [4000, 12000],
            "recovery_days": 10,
            "risk_level": "low",
        },
        "chin-augmentation-001": {
            "name": "Chin Augmentation",
            "typical_cost_range": [3500, 9000],
            "recovery_days": 7,
            "risk_level": "low",
        },
    }
    
    data = procedure_data.get(procedure_id, {
        "name": "Unknown Procedure",
        "typical_cost_range": [5000, 15000],
        "recovery_days": 14,
        "risk_level": "medium",
    })
    
    return {
        "id": procedure_id,
        "name": data["name"],
        "category": "facial",
        "description": f"Description for {procedure_id}",
        "typical_cost_range": data["typical_cost_range"],
        "recovery_days": data["recovery_days"],
        "risk_level": data["risk_level"],
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
async def test_property_14_comparison_data_completeness(test_data):
    """
    Feature: docwiz-surgical-platform, Property 14: Comparison data completeness
    
    Validates: Requirements 4.3
    
    For any procedure comparison, the output should include cost differences,
    recovery time differences, and risk profile differences for all compared procedures.
    
    This test verifies that:
    1. The comparison result contains cost_differences
    2. The comparison result contains recovery_differences
    3. The comparison result contains risk_differences
    4. All pairwise comparisons are present
    5. Differences are calculated correctly
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
            patient_id=patient_id,
        )
        
        # Property 1: Comparison should contain cost_differences
        assert "cost_differences" in comparison, \
            "Comparison result missing cost_differences"
        assert isinstance(comparison["cost_differences"], dict), \
            "cost_differences should be a dictionary"
        
        # Property 2: Comparison should contain recovery_differences
        assert "recovery_differences" in comparison, \
            "Comparison result missing recovery_differences"
        assert isinstance(comparison["recovery_differences"], dict), \
            "recovery_differences should be a dictionary"
        
        # Property 3: Comparison should contain risk_differences
        assert "risk_differences" in comparison, \
            "Comparison result missing risk_differences"
        assert isinstance(comparison["risk_differences"], dict), \
            "risk_differences should be a dictionary"
        
        # Property 4: All pairwise comparisons should be present
        num_procedures = len(procedure_ids)
        expected_pairs = (num_procedures * (num_procedures - 1)) // 2
        
        assert len(comparison["cost_differences"]) == expected_pairs, \
            f"Expected {expected_pairs} cost comparisons, got {len(comparison['cost_differences'])}"
        assert len(comparison["recovery_differences"]) == expected_pairs, \
            f"Expected {expected_pairs} recovery comparisons, got {len(comparison['recovery_differences'])}"
        assert len(comparison["risk_differences"]) == expected_pairs, \
            f"Expected {expected_pairs} risk comparisons, got {len(comparison['risk_differences'])}"
        
        # Property 5: Verify differences are calculated correctly
        procedures = comparison["procedures"]
        
        # Check cost differences
        for i, proc1 in enumerate(procedures):
            for proc2 in procedures[i + 1:]:
                key = f"{proc1['procedure_name']}_vs_{proc2['procedure_name']}"
                
                # Cost difference should be absolute difference
                expected_cost_diff = abs(proc1["cost"] - proc2["cost"])
                actual_cost_diff = comparison["cost_differences"][key]
                assert abs(actual_cost_diff - expected_cost_diff) < 0.01, \
                    f"Cost difference incorrect for {key}: expected {expected_cost_diff}, got {actual_cost_diff}"
                
                # Recovery difference should be absolute difference
                expected_recovery_diff = abs(proc1["recovery_days"] - proc2["recovery_days"])
                actual_recovery_diff = comparison["recovery_differences"][key]
                assert actual_recovery_diff == expected_recovery_diff, \
                    f"Recovery difference incorrect for {key}: expected {expected_recovery_diff}, got {actual_recovery_diff}"
                
                # Risk difference should be a descriptive string
                risk_diff = comparison["risk_differences"][key]
                assert isinstance(risk_diff, str), \
                    f"Risk difference should be a string, got {type(risk_diff)}"
                assert len(risk_diff) > 0, \
                    f"Risk difference should not be empty for {key}"


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
async def test_comparison_differences_are_non_negative(source_image_id, procedure_ids):
    """
    Test that cost and recovery differences are non-negative.
    
    This verifies that differences are calculated as absolute values.
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
        
        # All cost differences should be non-negative
        for key, diff in comparison["cost_differences"].items():
            assert diff >= 0, f"Cost difference {key} is negative: {diff}"
        
        # All recovery differences should be non-negative
        for key, diff in comparison["recovery_differences"].items():
            assert diff >= 0, f"Recovery difference {key} is negative: {diff}"


@given(
    source_image_id=st.uuids().map(lambda x: x.hex),
    procedure_ids=procedure_id_list(min_size=3, max_size=3)
)
@settings(
    max_examples=30,
    deadline=10000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_comparison_with_three_procedures_has_three_pairs(source_image_id, procedure_ids):
    """
    Test that comparing 3 procedures produces exactly 3 pairwise comparisons.
    
    This verifies the combinatorial logic: C(3,2) = 3.
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
        
        # Should have exactly 3 pairwise comparisons
        assert len(comparison["cost_differences"]) == 3, \
            f"Expected 3 cost comparisons, got {len(comparison['cost_differences'])}"
        assert len(comparison["recovery_differences"]) == 3, \
            f"Expected 3 recovery comparisons, got {len(comparison['recovery_differences'])}"
        assert len(comparison["risk_differences"]) == 3, \
            f"Expected 3 risk comparisons, got {len(comparison['risk_differences'])}"
