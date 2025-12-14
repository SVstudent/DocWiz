"""Property-based tests for comparison persistence round-trip."""
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
async def test_property_15_comparison_persistence_round_trip(test_data):
    """
    Feature: docwiz-surgical-platform, Property 15: Comparison persistence round-trip
    
    Validates: Requirements 4.4
    
    For any saved comparison, retrieving it from storage should return a comparison
    set with the same procedures, visualizations, and metadata.
    
    This test verifies that:
    1. A comparison can be created and saved
    2. The comparison can be retrieved by ID
    3. Retrieved comparison has the same source_image_id
    4. Retrieved comparison has the same number of procedures
    5. Retrieved comparison has the same procedure IDs
    6. Retrieved comparison has the same metadata fields
    7. Retrieved comparison has the same difference calculations
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
    
    # Mock Firestore with in-memory storage
    stored_comparisons = {}
    
    from unittest.mock import patch
    with patch('app.services.comparison_service.get_db') as mock_get_db:
        mock_db = MagicMock()
        
        # Mock collection and document for saving
        def mock_collection(collection_name):
            mock_coll = MagicMock()
            
            def mock_document(doc_id):
                mock_doc = MagicMock()
                
                # Mock set method to store data
                def mock_set(data):
                    stored_comparisons[doc_id] = data
                
                mock_doc.set = mock_set
                
                # Mock get method to retrieve data
                def mock_get():
                    mock_doc_snapshot = MagicMock()
                    if doc_id in stored_comparisons:
                        mock_doc_snapshot.exists = True
                        mock_doc_snapshot.to_dict.return_value = stored_comparisons[doc_id]
                    else:
                        mock_doc_snapshot.exists = False
                    return mock_doc_snapshot
                
                mock_doc.get = mock_get
                
                return mock_doc
            
            mock_coll.document = mock_document
            return mock_coll
        
        mock_db.collection = mock_collection
        mock_get_db.return_value = mock_db
        
        # Step 1: Create and save comparison
        created_comparison = await service.create_comparison(
            source_image_id=source_image_id,
            procedure_ids=procedure_ids,
            patient_id=patient_id,
        )
        
        comparison_id = created_comparison["id"]
        
        # Step 2: Retrieve the comparison
        retrieved_comparison = await service.get_comparison(comparison_id)
        
        # Property 1: Retrieved comparison should not be None
        assert retrieved_comparison is not None, \
            "Retrieved comparison should not be None"
        
        # Property 2: Retrieved comparison should have the same ID
        assert retrieved_comparison["id"] == comparison_id, \
            f"Retrieved comparison ID mismatch: {retrieved_comparison['id']} != {comparison_id}"
        
        # Property 3: Retrieved comparison should have the same source_image_id
        assert retrieved_comparison["source_image_id"] == source_image_id, \
            f"Source image ID mismatch: {retrieved_comparison['source_image_id']} != {source_image_id}"
        
        # Property 4: Retrieved comparison should have the same patient_id
        assert retrieved_comparison["patient_id"] == patient_id, \
            f"Patient ID mismatch: {retrieved_comparison['patient_id']} != {patient_id}"
        
        # Property 5: Retrieved comparison should have the same number of procedures
        assert len(retrieved_comparison["procedures"]) == len(created_comparison["procedures"]), \
            f"Procedure count mismatch: {len(retrieved_comparison['procedures'])} != {len(created_comparison['procedures'])}"
        
        # Property 6: Retrieved comparison should have the same procedure IDs
        created_proc_ids = {p["procedure_id"] for p in created_comparison["procedures"]}
        retrieved_proc_ids = {p["procedure_id"] for p in retrieved_comparison["procedures"]}
        assert created_proc_ids == retrieved_proc_ids, \
            f"Procedure IDs mismatch: {retrieved_proc_ids} != {created_proc_ids}"
        
        # Property 7: Retrieved comparison should have the same metadata fields
        assert "cost_differences" in retrieved_comparison, \
            "Retrieved comparison missing cost_differences"
        assert "recovery_differences" in retrieved_comparison, \
            "Retrieved comparison missing recovery_differences"
        assert "risk_differences" in retrieved_comparison, \
            "Retrieved comparison missing risk_differences"
        assert "created_at" in retrieved_comparison, \
            "Retrieved comparison missing created_at"
        assert "metadata" in retrieved_comparison, \
            "Retrieved comparison missing metadata"
        
        # Property 8: Retrieved comparison should have the same difference calculations
        assert retrieved_comparison["cost_differences"] == created_comparison["cost_differences"], \
            "Cost differences mismatch after retrieval"
        assert retrieved_comparison["recovery_differences"] == created_comparison["recovery_differences"], \
            "Recovery differences mismatch after retrieval"
        assert retrieved_comparison["risk_differences"] == created_comparison["risk_differences"], \
            "Risk differences mismatch after retrieval"


@given(
    source_image_id=st.uuids().map(lambda x: x.hex),
    procedure_ids=procedure_id_list(min_size=2, max_size=3)
)
@settings(
    max_examples=50,
    deadline=10000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_comparison_retrieval_with_nonexistent_id_returns_none(source_image_id, procedure_ids):
    """
    Test that retrieving a non-existent comparison returns None.
    
    This verifies proper error handling for missing comparisons.
    """
    service, _, _ = create_comparison_service_with_mocks()
    
    # Mock Firestore to return non-existent document
    from unittest.mock import patch
    with patch('app.services.comparison_service.get_db') as mock_get_db:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_document = MagicMock()
        mock_doc_snapshot = MagicMock()
        
        mock_doc_snapshot.exists = False
        mock_document.get.return_value = mock_doc_snapshot
        mock_collection.document.return_value = mock_document
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Try to retrieve non-existent comparison
        nonexistent_id = str(uuid.uuid4())
        result = await service.get_comparison(nonexistent_id)
        
        # Should return None
        assert result is None, \
            f"Expected None for non-existent comparison, got {result}"


@given(test_data=comparison_test_data())
@settings(
    max_examples=30,
    deadline=10000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
@pytest.mark.property_test
async def test_comparison_visualization_ids_are_preserved(test_data):
    """
    Test that visualization IDs are preserved in the round-trip.
    
    This verifies that the generated visualization IDs are stored and retrieved correctly.
    """
    service, mock_viz_service, mock_proc_service = create_comparison_service_with_mocks()
    
    source_image_id = test_data["source_image_id"]
    procedure_ids = test_data["procedure_ids"]
    patient_id = test_data["patient_id"]
    
    # Setup mocks
    async def mock_get_procedure(proc_id):
        proc_dict = create_mock_procedure(proc_id)
        mock_model = MagicMock()
        mock_model.model_dump.return_value = proc_dict
        return mock_model
    
    mock_proc_service.get_procedure_by_id.side_effect = mock_get_procedure
    
    # Track generated visualization IDs
    generated_viz_ids = []
    
    async def mock_generate_preview(image_id, procedure_id, patient_id=None):
        viz_id = str(uuid.uuid4())
        generated_viz_ids.append(viz_id)
        procedure = create_mock_procedure(procedure_id)
        return create_mock_visualization(
            viz_id,
            image_id,
            procedure_id,
            procedure["name"]
        )
    
    mock_viz_service.generate_surgical_preview.side_effect = mock_generate_preview
    
    # Mock Firestore with in-memory storage
    stored_comparisons = {}
    
    from unittest.mock import patch
    with patch('app.services.comparison_service.get_db') as mock_get_db:
        mock_db = MagicMock()
        
        def mock_collection(collection_name):
            mock_coll = MagicMock()
            
            def mock_document(doc_id):
                mock_doc = MagicMock()
                
                def mock_set(data):
                    stored_comparisons[doc_id] = data
                
                mock_doc.set = mock_set
                
                def mock_get():
                    mock_doc_snapshot = MagicMock()
                    if doc_id in stored_comparisons:
                        mock_doc_snapshot.exists = True
                        mock_doc_snapshot.to_dict.return_value = stored_comparisons[doc_id]
                    else:
                        mock_doc_snapshot.exists = False
                    return mock_doc_snapshot
                
                mock_doc.get = mock_get
                
                return mock_doc
            
            mock_coll.document = mock_document
            return mock_coll
        
        mock_db.collection = mock_collection
        mock_get_db.return_value = mock_db
        
        # Create comparison
        created_comparison = await service.create_comparison(
            source_image_id=source_image_id,
            procedure_ids=procedure_ids,
            patient_id=patient_id,
        )
        
        comparison_id = created_comparison["id"]
        
        # Retrieve comparison
        retrieved_comparison = await service.get_comparison(comparison_id)
        
        # Extract visualization IDs from created and retrieved comparisons
        created_viz_ids = {p["visualization_id"] for p in created_comparison["procedures"]}
        retrieved_viz_ids = {p["visualization_id"] for p in retrieved_comparison["procedures"]}
        
        # Visualization IDs should be preserved
        assert created_viz_ids == retrieved_viz_ids, \
            f"Visualization IDs not preserved: {retrieved_viz_ids} != {created_viz_ids}"
        
        # All generated visualization IDs should be present
        assert set(generated_viz_ids) == created_viz_ids, \
            f"Generated visualization IDs not all present: {created_viz_ids} != {set(generated_viz_ids)}"
