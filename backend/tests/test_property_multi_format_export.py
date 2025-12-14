"""Property-based tests for multi-format export support.

Feature: docwiz-surgical-platform, Property 31: Multi-format export support

For any export operation, the system should be capable of generating output in
PDF, PNG, JPEG, and JSON formats.

Validates: Requirements 10.2
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
async def test_multi_format_export_support(mock_firestore):
    """
    Feature: docwiz-surgical-platform, Property 31: Multi-format export support
    
    For any export operation, the system should be capable of generating output in
    PDF, PNG, JPEG, and JSON formats.
    
    Validates: Requirements 10.2
    """
    # Create patient profile
    patient = PatientProfileModel(
        id="test-patient-1",
        user_id="test-user-1",
        name="Test Patient",
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
    
    # Test all supported formats
    formats = ["pdf", "png", "jpeg", "json"]
    
    for format in formats:
        # PROPERTY: System should be capable of generating output in each format
        export_bytes = await export_service.export_comprehensive_report(
            patient_id=patient.id,
            format=format,
            shareable=False,
            include_visualizations=True,
            include_cost_estimates=False,
            include_comparisons=False,
        )
        
        # Verify export was generated
        assert export_bytes is not None, f"Export in {format} format should not be None"
        assert len(export_bytes) > 0, f"Export in {format} format should not be empty"
        
        # Format-specific validation
        if format == "json":
            # JSON should be parseable
            export_data = json.loads(export_bytes.decode('utf-8'))
            assert isinstance(export_data, dict), "JSON export should be a dictionary"
            assert 'visualizations' in export_data, "JSON export should contain visualizations"
        
        elif format == "pdf":
            # PDF should start with PDF magic bytes
            assert export_bytes.startswith(b'%PDF'), "PDF export should start with PDF header"
        
        elif format in ["png", "jpeg"]:
            # Image formats should have appropriate magic bytes
            if format == "png":
                assert export_bytes.startswith(b'\x89PNG'), "PNG export should start with PNG header"
            elif format == "jpeg":
                assert export_bytes.startswith(b'\xff\xd8\xff'), "JPEG export should start with JPEG header"


@pytest.mark.asyncio
async def test_unsupported_format_raises_error(mock_firestore):
    """
    Test that unsupported formats raise appropriate errors.
    """
    # Create patient profile
    patient = PatientProfileModel(
        id="test-patient-1",
        user_id="test-user-1",
        name="Test Patient",
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
    
    # Test unsupported format
    with pytest.raises(ValueError, match="Unsupported export format"):
        await export_service.export_comprehensive_report(
            patient_id=patient.id,
            format="xml",  # Unsupported format
            shareable=False,
            include_visualizations=True,
            include_cost_estimates=False,
            include_comparisons=False,
        )
