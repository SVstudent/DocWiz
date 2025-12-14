"""Property-based tests for export metadata inclusion.

Feature: docwiz-surgical-platform, Property 32: Export metadata inclusion

For any generated export file, it should include a timestamp, patient name,
and unique report identifier in the metadata or header.

Validates: Requirements 10.3
"""
import pytest
from datetime import datetime
import json

from app.services.export_service import ExportService
from app.db.firestore_models import (
    PatientProfileModel,
    VisualizationResultModel,
    LocationModel,
    InsuranceInfoModel,
    create_document,
)
from app.db.base import Collections


@pytest.mark.asyncio
async def test_export_metadata_inclusion(mock_firestore):
    """
    Feature: docwiz-surgical-platform, Property 32: Export metadata inclusion
    
    For any generated export file, it should include a timestamp, patient name,
    and unique report identifier in the metadata or header.
    
    Validates: Requirements 10.3
    """
    # Create patient profile
    patient = PatientProfileModel(
        id="test-patient-1",
        user_id="test-user-1",
        name="John Doe",
        date_of_birth=datetime(1990, 1, 1).date(),
        location=LocationModel(
            zip_code="12345",
            city="Test City",
            state="NY",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Blue Cross",
            encrypted_policy_number="BC123456",
            group_number="GRP123",
            plan_type="PPO"
        ),
        version=1
    )
    await create_document(mock_firestore, Collections.PATIENT_PROFILES, patient)
    
    # Create a visualization
    viz = VisualizationResultModel(
        id="viz-1",
        patient_id=patient.id,
        procedure_id="proc-1",
        procedure_name="Rhinoplasty",
        before_image_url="https://storage.example.com/before_1.jpg",
        after_image_url="https://storage.example.com/after_1.jpg",
        prompt_used="Test prompt",
        confidence_score=0.9,
        metadata={}
    )
    await create_document(mock_firestore, Collections.VISUALIZATION_RESULTS, viz)
    
    # Create export service
    export_service = ExportService(mock_firestore)
    
    # Test JSON format (easiest to parse metadata)
    export_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="json",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=False,
        include_comparisons=False,
    )
    
    # Parse JSON
    export_data = json.loads(export_bytes.decode('utf-8'))
    
    # PROPERTY: Export should include patient name
    assert 'patient_name' in export_data, "Export should include patient_name"
    assert export_data['patient_name'] == "John Doe", "Patient name should match"
    
    # PROPERTY: Export should include timestamp
    assert 'generated_at' in export_data, "Export should include generated_at timestamp"
    assert export_data['generated_at'] is not None, "Timestamp should not be None"
    
    # PROPERTY: Export should include unique report identifier
    assert 'export_id' in export_data, "Export should include export_id"
    assert export_data['export_id'] is not None, "Export ID should not be None"
    assert len(export_data['export_id']) > 0, "Export ID should not be empty"
    
    # Test PDF format (verify it's generated with content)
    pdf_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="pdf",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=False,
        include_comparisons=False,
    )
    
    # PDF should be generated and not empty
    assert pdf_bytes is not None, "PDF should be generated"
    assert len(pdf_bytes) > 0, "PDF should not be empty"
    assert pdf_bytes.startswith(b'%PDF'), "Should be a valid PDF"
