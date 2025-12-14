"""Property-based tests for dual format claim output.

Feature: docwiz-surgical-platform, Property 24: Dual format claim output
Validates: Requirements 7.2

For any claim document generation, the system should produce both a PDF file
and structured data (JSON) as output.
"""
import json
import pytest
from datetime import datetime
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock

from app.services.insurance_doc_service import InsuranceDocService
from app.db.firestore_models import (
    PreAuthFormModel,
    ProcedureModel,
    PatientProfileModel,
    LocationModel,
    InsuranceInfoModel,
    ProviderInfoModel,
)


# Reuse strategies from previous tests
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
async def test_dual_format_claim_output(procedure, patient):
    """
    Feature: docwiz-surgical-platform, Property 24: Dual format claim output
    
    For any claim document generation, the system should produce both a PDF file
    and structured data (JSON) as output.
    
    Validates: Requirements 7.2
    """
    # Create mock database client
    mock_db = MagicMock()
    
    # Create mock Nano Banana client
    mock_nano_banana = AsyncMock()
    mock_nano_banana.generate_medical_justification = AsyncMock(
        return_value="Medical justification text for the procedure."
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
        form = await service.generate_preauth_form(
            procedure_id=procedure.id,
            patient_id=patient.id
        )
        
        # Mock get_preauth_form to return the generated form
        async def mock_get_preauth_form(form_id):
            if form_id == form.id:
                return form
            return None
        
        service.get_preauth_form = mock_get_preauth_form
        
        # Property: The system should produce a PDF file
        pdf_output = await service.export_preauth_form_pdf(form.id)
        
        assert pdf_output is not None, "PDF output must be generated"
        assert isinstance(pdf_output, bytes), "PDF output must be bytes"
        assert len(pdf_output) > 0, "PDF output must not be empty"
        
        # Verify PDF header (PDF files start with %PDF-)
        assert pdf_output[:4] == b'%PDF', "PDF output must have valid PDF header"
        
        # Property: The system should produce structured data (JSON)
        json_output = await service.export_preauth_form_json(form.id)
        
        assert json_output is not None, "JSON output must be generated"
        assert isinstance(json_output, str), "JSON output must be a string"
        assert len(json_output) > 0, "JSON output must not be empty"
        
        # Verify JSON is valid and parseable
        try:
            parsed_json = json.loads(json_output)
            assert isinstance(parsed_json, dict), "Parsed JSON must be a dictionary"
        except json.JSONDecodeError:
            pytest.fail("JSON output must be valid JSON")
        
        # Property: Both formats should contain the same core information
        # Verify JSON contains essential fields
        assert "form_id" in parsed_json, "JSON must contain form_id"
        assert "patient" in parsed_json, "JSON must contain patient information"
        assert "provider" in parsed_json, "JSON must contain provider information"
        assert "procedure" in parsed_json, "JSON must contain procedure information"
        assert "medical_justification" in parsed_json, "JSON must contain medical justification"
        
        # Verify form ID matches
        assert parsed_json["form_id"] == form.id, "JSON form_id must match generated form"
        
    finally:
        # Restore original functions
        service_module.get_document = original_get
        service_module.create_document = original_create


@pytest.mark.asyncio
async def test_dual_format_claim_output_example():
    """Example test case for dual format claim output."""
    # Create test data
    procedure = ProcedureModel(
        id="proc-789",
        name="Cleft Lip Repair",
        category="reconstructive",
        description="Surgical repair of cleft lip deformity",
        typical_cost_min=8000.0,
        typical_cost_max=18000.0,
        recovery_days=28,
        risk_level="medium",
        cpt_codes=["40700", "40701"],
        icd10_codes=["Q36.0", "Q36.9"],
        prompt_template="Generate cleft lip repair preview"
    )
    
    patient = PatientProfileModel(
        id="patient-789",
        user_id="user-789",
        name="Baby Johnson",
        date_of_birth=datetime(2023, 3, 15),
        location=LocationModel(
            zip_code="60601",
            city="Chicago",
            state="IL",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="UnitedHealthcare",
            encrypted_policy_number="UHC555666",
            group_number="GRP999",
            plan_type="PPO"
        )
    )
    
    # Create mock database and Nano Banana client
    mock_db = MagicMock()
    mock_nano_banana = AsyncMock()
    mock_nano_banana.generate_medical_justification = AsyncMock(
        return_value="Cleft lip repair is medically necessary for functional and aesthetic restoration."
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
        form = await service.generate_preauth_form(
            procedure_id=procedure.id,
            patient_id=patient.id
        )
        
        # Mock get_preauth_form to return the generated form
        async def mock_get_preauth_form(form_id):
            if form_id == form.id:
                return form
            return None
        
        service.get_preauth_form = mock_get_preauth_form
        
        # Export as PDF
        pdf_bytes = await service.export_preauth_form_pdf(form.id)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
        
        # Export as JSON
        json_str = await service.export_preauth_form_json(form.id)
        assert len(json_str) > 0
        
        # Parse and verify JSON
        json_data = json.loads(json_str)
        assert json_data["form_id"] == form.id
        assert json_data["patient"]["name"] == "Baby Johnson"
        assert json_data["provider"]["name"] == "DocWiz Surgical Center"
        assert json_data["procedure"]["name"] == "Cleft Lip Repair"
        assert len(json_data["diagnosis_codes"]["cpt"]) == 2
        
    finally:
        service_module.get_document = original_get
        service_module.create_document = original_create
