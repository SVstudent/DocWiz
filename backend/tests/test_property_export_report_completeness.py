"""Property-based tests for export report completeness.

Feature: docwiz-surgical-platform, Property 30: Export report completeness

For any export request, the generated report should include all patient visualizations,
all cost estimates, and all saved comparisons.

Validates: Requirements 10.1
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
from decimal import Decimal
import json

from app.services.export_service import ExportService
from app.db.firestore_models import (
    PatientProfileModel,
    VisualizationResultModel,
    CostBreakdownModel,
    ComparisonSetModel,
    LocationModel,
    InsuranceInfoModel,
    ProviderInfoModel,
    create_document,
)
from app.db.base import Collections


# Custom strategies
@st.composite
def patient_profile_strategy(draw):
    """Generate random patient profile."""
    return PatientProfileModel(
        id=draw(st.uuids()).hex,
        user_id=draw(st.uuids()).hex,
        name=draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'Nd', ' ')))),
        date_of_birth=draw(st.dates(min_value=datetime(1920, 1, 1).date(), max_value=datetime(2010, 1, 1).date())),
        location=LocationModel(
            zip_code=draw(st.text(min_size=5, max_size=5, alphabet=st.characters(whitelist_categories=('Nd',)))),
            city=draw(st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', ' ')))),
            state=draw(st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',)))),
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider=draw(st.sampled_from(["Blue Cross", "Aetna", "UnitedHealthcare", "Cigna"])),
            encrypted_policy_number=draw(st.text(min_size=8, max_size=20)),
            group_number=draw(st.text(min_size=5, max_size=15)),
            plan_type=draw(st.sampled_from(["PPO", "HMO", "EPO"]))
        ),
        encrypted_medical_history=None,
        version=1
    )


@st.composite
def visualization_strategy(draw, patient_id: str):
    """Generate random visualization result."""
    return VisualizationResultModel(
        id=draw(st.uuids()).hex,
        patient_id=patient_id,
        procedure_id=draw(st.uuids()).hex,
        procedure_name=draw(st.sampled_from(["Rhinoplasty", "Breast Augmentation", "Facelift"])),
        before_image_url=f"https://storage.example.com/before_{draw(st.uuids()).hex}.jpg",
        after_image_url=f"https://storage.example.com/after_{draw(st.uuids()).hex}.jpg",
        prompt_used=draw(st.text(min_size=10, max_size=200)),
        confidence_score=draw(st.floats(min_value=0.5, max_value=1.0)),
        metadata={}
    )


@st.composite
def cost_breakdown_strategy(draw, patient_id: str):
    """Generate random cost breakdown."""
    surgeon_fee = Decimal(str(draw(st.integers(min_value=2000, max_value=15000))))
    facility_fee = Decimal(str(draw(st.integers(min_value=1000, max_value=8000))))
    anesthesia_fee = Decimal(str(draw(st.integers(min_value=500, max_value=3000))))
    post_op_care = Decimal(str(draw(st.integers(min_value=500, max_value=2000))))
    total_cost = surgeon_fee + facility_fee + anesthesia_fee + post_op_care
    
    return CostBreakdownModel(
        id=draw(st.uuids()).hex,
        procedure_id=draw(st.uuids()).hex,
        patient_id=patient_id,
        surgeon_fee=float(surgeon_fee),
        facility_fee=float(facility_fee),
        anesthesia_fee=float(anesthesia_fee),
        post_op_care=float(post_op_care),
        total_cost=float(total_cost),
        insurance_coverage=None,
        patient_responsibility=float(total_cost),
        deductible=0.0,
        copay=0.0,
        out_of_pocket_max=10000.0,
        payment_plans=[],
        data_sources=["Test data source"],
        region="Northeast"
    )


@st.composite
def comparison_strategy(draw, patient_id: str):
    """Generate random comparison set."""
    num_procedures = draw(st.integers(min_value=2, max_value=4))
    return ComparisonSetModel(
        id=draw(st.uuids()).hex,
        patient_id=patient_id,
        source_image_id=draw(st.uuids()).hex,
        procedure_ids=[draw(st.uuids()).hex for _ in range(num_procedures)],
        visualization_ids=[draw(st.uuids()).hex for _ in range(num_procedures)],
        cost_breakdown_ids=[],
        metadata={}
    )


@pytest.mark.asyncio
async def test_export_report_completeness_simple(mock_firestore):
    """
    Feature: docwiz-surgical-platform, Property 30: Export report completeness
    
    For any export request, the generated report should include all patient visualizations,
    all cost estimates, and all saved comparisons.
    
    Validates: Requirements 10.1
    
    This is a simplified version that tests with fixed counts.
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
    
    # Create 2 visualizations
    viz1 = VisualizationResultModel(
        id="viz-1",
        patient_id=patient.id,
        procedure_id="proc-1",
        procedure_name="Rhinoplasty",
        before_image_url="https://storage.example.com/before_1.jpg",
        after_image_url="https://storage.example.com/after_1.jpg",
        prompt_used="Test prompt 1",
        confidence_score=0.9,
        metadata={}
    )
    await create_document(mock_firestore, Collections.VISUALIZATION_RESULTS, viz1)
    
    viz2 = VisualizationResultModel(
        id="viz-2",
        patient_id=patient.id,
        procedure_id="proc-2",
        procedure_name="Facelift",
        before_image_url="https://storage.example.com/before_2.jpg",
        after_image_url="https://storage.example.com/after_2.jpg",
        prompt_used="Test prompt 2",
        confidence_score=0.85,
        metadata={}
    )
    await create_document(mock_firestore, Collections.VISUALIZATION_RESULTS, viz2)
    
    # Create 2 cost estimates
    cost1 = CostBreakdownModel(
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
    await create_document(mock_firestore, Collections.COST_BREAKDOWNS, cost1)
    
    cost2 = CostBreakdownModel(
        id="cost-2",
        procedure_id="proc-2",
        patient_id=patient.id,
        surgeon_fee=8000.0,
        facility_fee=4000.0,
        anesthesia_fee=2000.0,
        post_op_care=1500.0,
        total_cost=15500.0,
        patient_responsibility=15500.0,
        deductible=0.0,
        copay=0.0,
        out_of_pocket_max=10000.0,
        payment_plans=[],
        data_sources=["Test source"],
        region="Northeast"
    )
    await create_document(mock_firestore, Collections.COST_BREAKDOWNS, cost2)
    
    # Create 1 comparison
    comparison1 = ComparisonSetModel(
        id="comp-1",
        patient_id=patient.id,
        source_image_id="img-1",
        procedure_ids=["proc-1", "proc-2"],
        visualization_ids=["viz-1", "viz-2"],
        cost_breakdown_ids=[],
        metadata={}
    )
    await create_document(mock_firestore, Collections.COMPARISON_SETS, comparison1)
    
    # Create export service
    export_service = ExportService(mock_firestore)
    
    # Generate export (JSON format for easy parsing)
    export_bytes = await export_service.export_comprehensive_report(
        patient_id=patient.id,
        format="json",
        shareable=False,
        include_visualizations=True,
        include_cost_estimates=True,
        include_comparisons=True,
    )
    
    # Parse JSON
    export_data = json.loads(export_bytes.decode('utf-8'))
    
    # PROPERTY: Export should include ALL visualizations
    assert len(export_data['visualizations']) == 2, \
        f"Expected 2 visualizations, got {len(export_data['visualizations'])}"
    
    # PROPERTY: Export should include ALL cost estimates
    assert len(export_data['cost_estimates']) == 2, \
        f"Expected 2 cost estimates, got {len(export_data['cost_estimates'])}"
    
    # PROPERTY: Export should include ALL comparisons
    assert len(export_data['comparisons']) == 1, \
        f"Expected 1 comparison, got {len(export_data['comparisons'])}"
    
    # Verify visualization IDs match
    export_viz_ids = {viz['id'] for viz in export_data['visualizations']}
    expected_viz_ids = {"viz-1", "viz-2"}
    assert export_viz_ids == expected_viz_ids, \
        "Export visualization IDs don't match expected IDs"
    
    # Verify cost estimate IDs match
    export_cost_ids = {cost['id'] for cost in export_data['cost_estimates']}
    expected_cost_ids = {"cost-1", "cost-2"}
    assert export_cost_ids == expected_cost_ids, \
        "Export cost estimate IDs don't match expected IDs"
    
    # Verify comparison IDs match
    export_comparison_ids = {comp['id'] for comp in export_data['comparisons']}
    expected_comparison_ids = {"comp-1"}
    assert export_comparison_ids == expected_comparison_ids, \
        "Export comparison IDs don't match expected IDs"
    
    # Verify disclaimer is present
    assert 'disclaimer' in export_data, "Export should include disclaimer"
    assert len(export_data['disclaimer']) > 0, "Disclaimer should not be empty"
