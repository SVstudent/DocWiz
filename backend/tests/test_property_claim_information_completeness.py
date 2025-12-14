"""Property-based tests for claim information completeness.

Feature: docwiz-surgical-platform, Property 25: Claim information completeness
Validates: Requirements 7.4

For any completed claim document, it should include patient information section,
provider information section, and procedure details section.
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


# Reuse strategies from previous test
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


@pytest.mark.asyncio
@given(
    procedure=procedure_strategy(),
    patient=patient_profile_strategy()
)
@settings(max_examples=100, deadline=None)
async def test_claim_information_completeness(procedure, patient):
    """
    Feature: docwiz-surgical-platform, Property 25: Claim information completeness
    
    For any completed claim document, it should include patient information section,
    provider information section, and procedure details section.
    
    Validates: Requirements 7.4
    """
    # Create mock database client
    mock_db = MagicMock()
    
    # Create mock Nano Banana client
    mock_nano_banana = AsyncMock()
    mock_nano_banana.generate_medical_justification = AsyncMock(
        return_value="Medical justification text."
    )
    
    # Create service
    service = InsuranceDocService(db=mock_db, nano_banana_client=mock_nano_banana)
    
    # Mock database get_document calls
    async def mock_get_document(db, collection, doc_id):
        if "procedures" in collection.lower():
            return procedure.model_dump()
        elif "patient" in collection.lower():
            return patient.model_dump()
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
        result = await service.generate_preauth_form(
            procedure_id=procedure.id,
            patient_id=patient.id
        )
        
        # Property: The claim document should include patient information section
        assert result.structured_data is not None, "Structured data must be present"
        assert "patient" in result.structured_data, "Patient information section must be present"
        
        patient_info = result.structured_data["patient"]
        assert "name" in patient_info, "Patient name must be present"
        assert "date_of_birth" in patient_info, "Patient date of birth must be present"
        assert "insurance_provider" in patient_info, "Insurance provider must be present"
        assert "policy_number" in patient_info, "Policy number must be present"
        
        # Verify patient data is not empty
        assert len(patient_info["name"]) > 0, "Patient name must not be empty"
        assert patient_info["insurance_provider"] is not None, "Insurance provider must not be None"
        
        # Property: The claim document should include provider information section
        assert "provider" in result.structured_data, "Provider information section must be present"
        
        provider_info = result.structured_data["provider"]
        assert "name" in provider_info, "Provider name must be present"
        assert "npi" in provider_info, "Provider NPI must be present"
        assert "address" in provider_info, "Provider address must be present"
        assert "phone" in provider_info, "Provider phone must be present"
        assert "specialty" in provider_info, "Provider specialty must be present"
        
        # Verify provider data is not empty
        assert len(provider_info["name"]) > 0, "Provider name must not be empty"
        assert len(provider_info["npi"]) > 0, "Provider NPI must not be empty"
        assert len(provider_info["address"]) > 0, "Provider address must not be empty"
        assert len(provider_info["phone"]) > 0, "Provider phone must not be empty"
        assert len(provider_info["specialty"]) > 0, "Provider specialty must not be empty"
        
        # Property: The claim document should include procedure details section
        assert "procedure" in result.structured_data, "Procedure details section must be present"
        
        procedure_info = result.structured_data["procedure"]
        assert "name" in procedure_info, "Procedure name must be present"
        assert "category" in procedure_info, "Procedure category must be present"
        assert "description" in procedure_info, "Procedure description must be present"
        assert "cpt_codes" in procedure_info, "CPT codes must be present"
        assert "icd10_codes" in procedure_info, "ICD-10 codes must be present"
        
        # Verify procedure data is not empty
        assert len(procedure_info["name"]) > 0, "Procedure name must not be empty"
        assert len(procedure_info["cpt_codes"]) > 0, "CPT codes list must not be empty"
        assert len(procedure_info["icd10_codes"]) > 0, "ICD-10 codes list must not be empty"
        
    finally:
        # Restore original functions
        service_module.get_document = original_get
        service_module.create_document = original_create


@pytest.mark.asyncio
async def test_claim_information_completeness_example():
    """Example test case for claim information completeness."""
    # Create test data
    procedure = ProcedureModel(
        id="proc-456",
        name="Breast Augmentation",
        category="body",
        description="Surgical breast enhancement",
        typical_cost_min=6000.0,
        typical_cost_max=12000.0,
        recovery_days=21,
        risk_level="medium",
        cpt_codes=["19325", "19340"],
        icd10_codes=["N62", "N64.82"],
        prompt_template="Generate breast augmentation preview"
    )
    
    patient = PatientProfileModel(
        id="patient-456",
        user_id="user-456",
        name="Jane Smith",
        date_of_birth=datetime(1985, 5, 15),
        location=LocationModel(
            zip_code="10001",
            city="New York",
            state="NY",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Aetna",
            encrypted_policy_number="AET987654",
            group_number="GRP456",
            plan_type="HMO"
        )
    )
    
    # Create mock database and Nano Banana client
    mock_db = MagicMock()
    mock_nano_banana = AsyncMock()
    mock_nano_banana.generate_medical_justification = AsyncMock(
        return_value="Breast augmentation is medically necessary for reconstruction."
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
        
        # Verify all three sections are present
        assert "patient" in result.structured_data
        assert "provider" in result.structured_data
        assert "procedure" in result.structured_data
        
        # Verify patient section completeness
        assert result.structured_data["patient"]["name"] == "Jane Smith"
        assert result.structured_data["patient"]["insurance_provider"] == "Aetna"
        
        # Verify provider section completeness
        assert len(result.structured_data["provider"]["name"]) > 0
        assert len(result.structured_data["provider"]["npi"]) > 0
        
        # Verify procedure section completeness
        assert result.structured_data["procedure"]["name"] == "Breast Augmentation"
        assert len(result.structured_data["procedure"]["cpt_codes"]) == 2
        
    finally:
        service_module.get_document = original_get
        service_module.create_document = original_create
