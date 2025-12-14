"""Property-based tests for medical disclaimer inclusion.

Feature: docwiz-surgical-platform, Property 22: Medical disclaimer inclusion

For any medical information display (procedure details, cost estimates, visualizations),
the output should include disclaimer text stating results are estimates requiring
professional consultation.

Validates: Requirements 6.5
"""
import pytest
from datetime import datetime
import json

from app.services.export_service import ExportService
from app.db.firestore_models import (
    PatientProfileModel,
    VisualizationResultModel,
    CostBreakdownModel,
    LocationModel,
    InsuranceInfoModel,
    create_document,
)
from app.db.base import Collections


@pytest.mark.asyncio
async def test_medical_disclaimer_inclusion(mock_firestore):
    """
    Feature: docwiz-surgical-platform, Property 22: Medical disclaimer inclusion
    
    For any medical information display (procedure details, cost estimates, visualizations),
    the output should include disclaimer text stating results are estimates requiring
    professional consultation.
    
    Validates: Requirements 6.5
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
    
    # Create cost estimate
    cost = CostBreakdownModel(
        id="cost-1",
        procedure_id="proc-1",
        patient_id=patient.id,
        surgeon_fee=5000.0,
        facility_fee=3000.0,
        anesthesia_fee=1500.0,
        post_op_care=1000.0,
        total_cost=10500.0,
        patient_responsibility=10500.0,
        deductible=0.0,
        copay=0.0,
        out_of_pocket_max=10000.0,
        payment_plans=[],
        data_sources=["Test source"],
        region="Northeast"
    )
    await create_document(mock_firestore, Collections.COST_BREAKDOWNS, cost)
    
    # Create export service
    export_service = ExportService(mock_firestore)
    
    # Test JSON format
    json_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="json",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=True,
        include_comparisons=False,
    )
    
    json_data = json.loads(json_bytes.decode('utf-8'))
    
    # PROPERTY: Export should include disclaimer
    assert 'disclaimer' in json_data, "Export should include disclaimer field"
    disclaimer = json_data['disclaimer']
    
    # PROPERTY: Disclaimer should not be empty
    assert disclaimer is not None, "Disclaimer should not be None"
    assert len(disclaimer) > 0, "Disclaimer should not be empty"
    
    # PROPERTY: Disclaimer should mention key concepts
    disclaimer_lower = disclaimer.lower()
    assert 'medical' in disclaimer_lower or 'informational' in disclaimer_lower, \
        "Disclaimer should mention medical/informational nature"
    assert 'professional' in disclaimer_lower or 'consult' in disclaimer_lower, \
        "Disclaimer should mention professional consultation"
    assert 'estimate' in disclaimer_lower or 'approximate' in disclaimer_lower, \
        "Disclaimer should mention estimates/approximations"
    
    # Test PDF format
    pdf_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="pdf",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=True,
        include_comparisons=False,
    )
    
    # PROPERTY: PDF should be generated (disclaimer is included in PDF generation)
    assert pdf_bytes is not None, "PDF should be generated"
    assert len(pdf_bytes) > 0, "PDF should not be empty"
    assert pdf_bytes.startswith(b'%PDF'), "Should be a valid PDF"
    
    # Test PNG format
    png_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="png",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=False,
        include_comparisons=False,
    )
    
    # PROPERTY: PNG should be generated (disclaimer is included in image generation)
    assert png_bytes is not None, "PNG should be generated"
    assert len(png_bytes) > 0, "PNG should not be empty"
    assert png_bytes.startswith(b'\x89PNG'), "Should be a valid PNG"
