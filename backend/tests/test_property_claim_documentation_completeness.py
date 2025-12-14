"""Property-based tests for claim documentation completeness.

Feature: docwiz-surgical-platform, Property 23: Claim documentation completeness
Validates: Requirements 7.1

For any insurance claim generation, the output should include procedure codes (CPT),
medical necessity justification, and cost breakdown.
"""
import pytest
from datetime import datetime
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock

from app.services.insurance_doc_service import InsuranceDocService
from app.db.firestore_models import (
    PreAuthFormModel,
    ProcedureModel,
    PatientProfileModel,
    CostBreakdownModel,
    LocationModel,
    InsuranceInfoModel,
    ProviderInfoModel,
)


# Custom strategies for generating test data
@st.composite
def procedure_strategy(draw):
    """Generate random procedure data."""
    return ProcedureModel(
        id=draw(st.uuids()).hex,
        name=draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        category=draw(st.sampled_from(["facial", "body", "reconstructive", "cosmetic"])),
        description=draw(st.text(min_size=20, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po')))),
        typical_cost_min=draw(st.floats(min_value=1000, max_value=50000)),
        typical_cost_max=draw(st.floats(min_value=50000, max_value=200000)),
        recovery_days=draw(st.integers(min_value=1, max_value=365)),
        risk_level=draw(st.sampled_from(["low", "medium", "high"])),
        cpt_codes=draw(st.lists(st.text(min_size=5, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))), min_size=1, max_size=5)),
        icd10_codes=draw(st.lists(st.text(min_size=3, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))), min_size=1, max_size=5)),
        prompt_template=draw(st.text(min_size=10, max_size=100))
    )


@st.composite
def patient_profile_strategy(draw):
    """Generate random patient profile data."""
    return PatientProfileModel(
        id=draw(st.uuids()).hex,
        user_id=draw(st.uuids()).hex,
        name=draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')))),
        date_of_birth=draw(st.datetimes(min_value=datetime(1920, 1, 1), max_value=datetime(2010, 12, 31))),
        location=LocationModel(
            zip_code=draw(st.text(min_size=5, max_size=5, alphabet=st.characters(whitelist_categories=('Nd',)))),
            city=draw(st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')))),
            state=draw(st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',)))),
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider=draw(st.sampled_from(["Blue Cross", "Aetna", "UnitedHealthcare", "Cigna"])),
            encrypted_policy_number=draw(st.text(min_size=10, max_size=20)),
            group_number=draw(st.text(min_size=5, max_size=15)),
            plan_type=draw(st.sampled_from(["PPO", "HMO", "EPO"]))
        ),
        encrypted_medical_history=draw(st.one_of(st.none(), st.text(min_size=10, max_size=200)))
    )


@st.composite
def cost_breakdown_strategy(draw):
    """Generate random cost breakdown data."""
    surgeon_fee = draw(st.floats(min_value=1000, max_value=50000))
    facility_fee = draw(st.floats(min_value=500, max_value=20000))
    anesthesia_fee = draw(st.floats(min_value=500, max_value=5000))
    post_op_care = draw(st.floats(min_value=200, max_value=5000))
    total_cost = surgeon_fee + facility_fee + anesthesia_fee + post_op_care
    
    return CostBreakdownModel(
        id=draw(st.uuids()).hex,
        procedure_id=draw(st.uuids()).hex,
        patient_id=draw(st.uuids()).hex,
        surgeon_fee=surgeon_fee,
        facility_fee=facility_fee,
        anesthesia_fee=anesthesia_fee,
        post_op_care=post_op_care,
        total_cost=total_cost,
        insurance_coverage=draw(st.floats(min_value=0, max_value=total_cost)),
        patient_responsibility=draw(st.floats(min_value=0, max_value=total_cost)),
        deductible=draw(st.floats(min_value=0, max_value=5000)),
        copay=draw(st.floats(min_value=0, max_value=1000)),
        out_of_pocket_max=draw(st.floats(min_value=1000, max_value=10000))
    )


@pytest.mark.asyncio
@given(
    procedure=procedure_strategy(),
    patient=patient_profile_strategy(),
    cost_breakdown=st.one_of(st.none(), cost_breakdown_strategy())
)
@settings(max_examples=100, deadline=None)
async def test_claim_documentation_completeness(procedure, patient, cost_breakdown):
    """
    Feature: docwiz-surgical-platform, Property 23: Claim documentation completeness
    
    For any insurance claim generation, the output should include procedure codes (CPT),
    medical necessity justification, and cost breakdown.
    
    Validates: Requirements 7.1
    """
    # Create mock database client
    mock_db = MagicMock()
    
    # Create mock Nano Banana client
    mock_nano_banana = AsyncMock()
    mock_nano_banana.generate_medical_justification = AsyncMock(
        return_value="This procedure is medically necessary for the patient's condition."
    )
    
    # Create service
    service = InsuranceDocService(db=mock_db, nano_banana_client=mock_nano_banana)
    
    # Mock database get_document calls
    async def mock_get_document(db, collection, doc_id):
        if "procedures" in collection.lower():
            return procedure.model_dump()
        elif "patient" in collection.lower():
            return patient.model_dump()
        elif "cost" in collection.lower() and cost_breakdown:
            return cost_breakdown.model_dump()
        return None
    
    # Mock create_document
    async def mock_create_document(db, collection, data):
        return data.id
    
    # Patch the functions
    import app.services.insurance_doc_service as service_module
    original_get = service_module.get_document
    original_create = service_module.create_document
    
    service_module.get_document = mock_get_document
    service_module.create_document = mock_create_document
    
    try:
        # Generate pre-auth form
        cost_breakdown_id = cost_breakdown.id if cost_breakdown else None
        result = await service.generate_preauth_form(
            procedure_id=procedure.id,
            patient_id=patient.id,
            cost_breakdown_id=cost_breakdown_id
        )
        
        # Property: The output should include procedure codes (CPT)
        assert result.cpt_codes is not None, "CPT codes must be present"
        assert len(result.cpt_codes) > 0, "CPT codes list must not be empty"
        assert all(isinstance(code, str) for code in result.cpt_codes), "All CPT codes must be strings"
        
        # Property: The output should include medical necessity justification
        assert result.medical_justification is not None, "Medical justification must be present"
        assert isinstance(result.medical_justification, str), "Medical justification must be a string"
        assert len(result.medical_justification) > 0, "Medical justification must not be empty"
        
        # Property: The output should include cost breakdown (in structured data if available)
        assert result.structured_data is not None, "Structured data must be present"
        assert isinstance(result.structured_data, dict), "Structured data must be a dictionary"
        
        # If cost breakdown was provided, it should be in structured data
        if cost_breakdown:
            assert "cost_estimate" in result.structured_data, "Cost estimate must be in structured data when cost breakdown provided"
            cost_data = result.structured_data["cost_estimate"]
            assert "total_cost" in cost_data, "Total cost must be present"
            assert "surgeon_fee" in cost_data, "Surgeon fee must be present"
            assert "facility_fee" in cost_data, "Facility fee must be present"
            assert "anesthesia_fee" in cost_data, "Anesthesia fee must be present"
            assert "post_op_care" in cost_data, "Post-op care must be present"
        
    finally:
        # Restore original functions
        service_module.get_document = original_get
        service_module.create_document = original_create


@pytest.mark.asyncio
async def test_claim_documentation_completeness_example():
    """Example test case for claim documentation completeness."""
    # Create test data
    procedure = ProcedureModel(
        id="proc-123",
        name="Rhinoplasty",
        category="facial",
        description="Surgical reshaping of the nose",
        typical_cost_min=5000.0,
        typical_cost_max=15000.0,
        recovery_days=14,
        risk_level="medium",
        cpt_codes=["30400", "30420"],
        icd10_codes=["J34.2", "M95.0"],
        prompt_template="Generate rhinoplasty preview"
    )
    
    patient = PatientProfileModel(
        id="patient-123",
        user_id="user-123",
        name="John Doe",
        date_of_birth=datetime(1990, 1, 1),
        location=LocationModel(
            zip_code="94102",
            city="San Francisco",
            state="CA",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Blue Cross",
            encrypted_policy_number="BC123456",
            group_number="GRP789",
            plan_type="PPO"
        )
    )
    
    # Create mock database and Nano Banana client
    mock_db = MagicMock()
    mock_nano_banana = AsyncMock()
    mock_nano_banana.generate_medical_justification = AsyncMock(
        return_value="Rhinoplasty is medically necessary to correct nasal obstruction."
    )
    
    # Create service
    service = InsuranceDocService(db=mock_db, nano_banana_client=mock_nano_banana)
    
    # Mock database functions
    async def mock_get_document(db, collection, doc_id):
        if "procedures" in collection.lower():
            return procedure.model_dump()
        elif "patient" in collection.lower():
            return patient.model_dump()
        return None
    
    async def mock_create_document(db, collection, data):
        return data.id
    
    import app.services.insurance_doc_service as service_module
    original_get = service_module.get_document
    original_create = service_module.create_document
    
    service_module.get_document = mock_get_document
    service_module.create_document = mock_create_document
    
    try:
        # Generate pre-auth form
        result = await service.generate_preauth_form(
            procedure_id=procedure.id,
            patient_id=patient.id
        )
        
        # Verify completeness
        assert len(result.cpt_codes) == 2
        assert "30400" in result.cpt_codes
        assert "30420" in result.cpt_codes
        assert len(result.medical_justification) > 0
        assert result.structured_data is not None
        
    finally:
        service_module.get_document = original_get
        service_module.create_document = original_create
