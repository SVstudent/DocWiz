"""Integration tests for insurance API endpoints."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.firestore_models import (
    ProcedureModel,
    PatientProfileModel,
    LocationModel,
    InsuranceInfoModel,
    PreAuthFormModel,
    ProviderInfoModel,
)


def test_validate_insurance_endpoint(client):
    """Test insurance validation endpoint."""
    # Mock authentication and validation
    from app.api.dependencies import get_current_active_user
    from app.db.models import User
    
    def mock_user():
        return User(id="test-user", email="test@example.com", hashed_password="fake")
    
    with patch('app.services.profile_service.ProfileService.validate_insurance_provider') as mock_validate:
        mock_validate.return_value = True
        
        # Override auth dependency
        from app.main import app
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            response = client.post(
                "/api/insurance/validate",
                json={
                    "provider": "Blue Cross",
                    "policy_number": "BC123456",
                    "group_number": "GRP789"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_valid"] is True
            assert data["provider"] == "Blue Cross"
        finally:
            app.dependency_overrides.clear()


def test_generate_claim_endpoint(client):
    """Test claim generation endpoint."""
    from app.api.dependencies import get_current_active_user
    from app.db.models import User
    
    def mock_user():
        return User(id="test-user", email="test@example.com", hashed_password="fake")
    
    # Create test data
    procedure = ProcedureModel(
        id="proc-test-123",
        name="Test Procedure",
        category="facial",
        description="Test description",
        typical_cost_min=5000.0,
        typical_cost_max=15000.0,
        recovery_days=14,
        risk_level="medium",
        cpt_codes=["12345"],
        icd10_codes=["A00.0"],
        prompt_template="Test template"
    )
    
    patient = PatientProfileModel(
        id="patient-test-123",
        user_id="user-test-123",
        name="Test Patient",
        date_of_birth=datetime(1990, 1, 1),
        location=LocationModel(
            zip_code="12345",
            city="Test City",
            state="TS",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Blue Cross",
            encrypted_policy_number="BC123456",
            group_number="GRP789",
            plan_type="PPO"
        )
    )
    
    # Mock the insurance service methods
    with patch('app.services.insurance_doc_service.get_document') as mock_get_doc, \
         patch('app.services.insurance_doc_service.create_document') as mock_create_doc, \
         patch('app.services.nano_banana_client.NanoBananaClient.generate_medical_justification') as mock_nano:
        
        # Setup mocks
        async def mock_get_document_impl(db, collection, doc_id):
            if "procedures" in collection.lower():
                return procedure.model_dump()
            elif "patient" in collection.lower():
                return patient.model_dump()
            return None
        
        async def mock_create_document_impl(db, collection, data):
            return data.id
        
        mock_get_doc.side_effect = mock_get_document_impl
        mock_create_doc.side_effect = mock_create_document_impl
        mock_nano.return_value = "Medical justification text"
        
        # Override auth dependency
        from app.main import app
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            response = client.post(
                "/api/insurance/claims",
                json={
                    "procedure_id": "proc-test-123",
                    "patient_id": "patient-test-123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["procedure_id"] == "proc-test-123"
            assert data["patient_id"] == "patient-test-123"
            assert len(data["cpt_codes"]) > 0
            assert len(data["medical_justification"]) > 0
        finally:
            app.dependency_overrides.clear()


def test_download_claim_pdf_endpoint(client):
    """Test PDF download endpoint."""
    from app.api.dependencies import get_current_active_user
    from app.db.models import User
    
    def mock_user():
        return User(id="test-user", email="test@example.com", hashed_password="fake")
    
    # Create test form
    form = PreAuthFormModel(
        id="form-test-123",
        patient_id="patient-test-123",
        procedure_id="proc-test-123",
        cpt_codes=["12345"],
        icd10_codes=["A00.0"],
        medical_justification="Test justification",
        provider_info=ProviderInfoModel(
            name="Test Provider",
            npi="1234567890",
            address="123 Test St",
            phone="555-1234",
            specialty="Test Specialty"
        ),
        structured_data={
            "patient": {"name": "Test Patient"},
            "provider": {"name": "Test Provider"},
            "procedure": {"name": "Test Procedure"}
        }
    )
    
    # Mock the insurance service methods
    with patch('app.services.insurance_doc_service.InsuranceDocService.export_preauth_form_pdf') as mock_export:
        mock_export.return_value = b'%PDF-1.4\ntest pdf content'
        
        # Override auth dependency
        from app.main import app
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            response = client.get("/api/insurance/claims/form-test-123/pdf")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert "attachment" in response.headers["content-disposition"]
            assert len(response.content) > 0
            # Verify PDF header
            assert response.content[:4] == b'%PDF'
        finally:
            app.dependency_overrides.clear()
