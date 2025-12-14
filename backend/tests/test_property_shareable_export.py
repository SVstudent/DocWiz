"""Property-based tests for shareable export sanitization.

Feature: docwiz-surgical-platform, Property 33: Shareable export sanitization

For any export with "shareable" option selected, the output should not contain
sensitive fields (policy number, medical history), while non-shareable exports
should include all data.

Validates: Requirements 10.5
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
async def test_shareable_export_sanitization(mock_firestore):
    """
    Feature: docwiz-surgical-platform, Property 33: Shareable export sanitization
    
    For any export with "shareable" option selected, the output should not contain
    sensitive fields (policy number, medical history), while non-shareable exports
    should include all data.
    
    Validates: Requirements 10.5
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
            encrypted_policy_number="SENSITIVE_POLICY_123",
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
    
    # Create cost estimate with insurance info
    cost = CostBreakdownModel(
        id="cost-1",
        procedure_id="proc-1",
        patient_id=patient.id,
        surgeon_fee=5000.0,
        facility_fee=3000.0,
        anesthesia_fee=1500.0,
        post_op_care=1000.0,
        total_cost=10500.0,
        insurance_coverage=8000.0,
        patient_responsibility=2500.0,
        deductible=1000.0,
        copay=1500.0,
        out_of_pocket_max=10000.0,
        payment_plans=[],
        data_sources=["Test source"],
        region="Northeast",
        insurance_provider="Blue Cross"
    )
    await create_document(mock_firestore, Collections.COST_BREAKDOWNS, cost)
    
    # Create export service
    export_service = ExportService(mock_firestore)
    
    # Test NON-shareable export (should include all data)
    non_shareable_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="json",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=True,
        include_comparisons=False,
    )
    
    non_shareable_data = json.loads(non_shareable_bytes.decode('utf-8'))
    
    # PROPERTY: Non-shareable export should include insurance information
    assert non_shareable_data['shareable'] == False, "Should be marked as non-shareable"
    cost_data = non_shareable_data['cost_estimates'][0]
    assert cost_data['insurance_provider'] == "Blue Cross", "Should include insurance provider"
    assert cost_data['insurance_coverage'] == 8000.0, "Should include insurance coverage"
    assert cost_data['deductible'] == 1000.0, "Should include deductible"
    assert cost_data['copay'] == 1500.0, "Should include copay"
    
    # Test SHAREABLE export (should sanitize sensitive data)
    shareable_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="json",
        shareable=True,
        include_visualizations=True,
        include_cost_estimates=True,
        include_comparisons=False,
    )
    
    shareable_data = json.loads(shareable_bytes.decode('utf-8'))
    
    # PROPERTY: Shareable export should be marked as shareable
    assert shareable_data['shareable'] == True, "Should be marked as shareable"
    
    # PROPERTY: Shareable export should sanitize insurance information
    shareable_cost_data = shareable_data['cost_estimates'][0]
    assert shareable_cost_data['insurance_provider'] == "REDACTED", "Insurance provider should be redacted"
    assert shareable_cost_data['insurance_coverage'] is None, "Insurance coverage should be removed"
    assert shareable_cost_data['deductible'] is None, "Deductible should be removed"
    assert shareable_cost_data['copay'] is None, "Copay should be removed"
    
    # PROPERTY: Shareable export should maintain visualizations (not sensitive)
    assert len(shareable_data['visualizations']) == 1, "Visualizations should be included"
    assert shareable_data['visualizations'][0]['id'] == "viz-1", "Visualization data should be intact"
