"""Property-based tests for cost breakdown completeness.

Feature: docwiz-surgical-platform, Property 8: Cost breakdown completeness

For any cost estimate calculation, the breakdown should include surgeon fee,
facility fee, anesthesia fee, and post-operative care as separate line items.

Validates: Requirements 3.1
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock

from app.services.cost_estimation_service import CostEstimationService
from app.schemas.profile import (
    PatientProfileResponse,
    LocationResponse,
    InsuranceInfoResponse,
)
from app.db.seed_pricing import PROCEDURE_BASE_PRICING


# Custom strategies
@st.composite
def patient_profile_strategy(draw):
    """Generate random patient profiles for testing."""
    # Valid ZIP codes from different regions
    zip_codes = ["10001", "30301", "60601", "75201", "94101"]
    
    # Valid insurance providers
    insurance_providers = [
        "Blue Cross Blue Shield",
        "Aetna",
        "UnitedHealthcare",
        "Cigna",
        "Kaiser Permanente",
        "Humana",
        "None",
    ]
    
    return PatientProfileResponse(
        id=str(draw(st.uuids())),
        user_id=str(draw(st.uuids())),
        name=draw(st.text(min_size=1, max_size=50)),
        date_of_birth=draw(st.dates(min_value=date(1920, 1, 1), max_value=date(2010, 1, 1))),
        location=LocationResponse(
            zip_code=draw(st.sampled_from(zip_codes)),
            city=draw(st.text(min_size=1, max_size=30)),
            state=draw(st.text(min_size=2, max_size=2)),
            country="USA",
        ),
        insurance_info=InsuranceInfoResponse(
            provider=draw(st.sampled_from(insurance_providers)),
            policy_number=draw(st.text(min_size=5, max_size=20)),
            group_number=draw(st.text(min_size=5, max_size=20)),
            plan_type=draw(st.sampled_from(["PPO", "HMO", "EPO"])),
            coverage_details={},
        ),
        medical_history=draw(st.text(max_size=200)),
        version=1,
        created_at=draw(st.datetimes()),
        updated_at=draw(st.datetimes()),
    )


@pytest.mark.asyncio
@given(
    procedure_id=st.sampled_from(list(PROCEDURE_BASE_PRICING.keys())),
    patient_profile=patient_profile_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_cost_breakdown_completeness(
    procedure_id: str,
    patient_profile: PatientProfileResponse,
    mock_firestore,
):
    """
    Feature: docwiz-surgical-platform, Property 8: Cost breakdown completeness
    
    For any cost estimate calculation, the breakdown should include surgeon fee,
    facility fee, anesthesia fee, and post-operative care as separate line items.
    
    Validates: Requirements 3.1
    """
    # Arrange - Create a fresh mock for each test
    mock_db = MagicMock()
    service = CostEstimationService(mock_db)
    
    # Act
    breakdown = await service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile,
    )
    
    # Assert - All required cost components must be present and non-negative
    assert breakdown.surgeon_fee is not None, "Surgeon fee must be present"
    assert breakdown.facility_fee is not None, "Facility fee must be present"
    assert breakdown.anesthesia_fee is not None, "Anesthesia fee must be present"
    assert breakdown.post_op_care is not None, "Post-op care fee must be present"
    
    # All fees should be non-negative
    assert breakdown.surgeon_fee >= Decimal("0.0"), "Surgeon fee must be non-negative"
    assert breakdown.facility_fee >= Decimal("0.0"), "Facility fee must be non-negative"
    assert breakdown.anesthesia_fee >= Decimal("0.0"), "Anesthesia fee must be non-negative"
    assert breakdown.post_op_care >= Decimal("0.0"), "Post-op care must be non-negative"
    
    # Total cost should equal sum of all components
    expected_total = (
        breakdown.surgeon_fee +
        breakdown.facility_fee +
        breakdown.anesthesia_fee +
        breakdown.post_op_care
    )
    assert breakdown.total_cost == expected_total, (
        f"Total cost {breakdown.total_cost} should equal sum of components {expected_total}"
    )
    
    # All components should be present as separate line items (not zero)
    assert breakdown.surgeon_fee > Decimal("0.0"), "Surgeon fee should be positive"
    assert breakdown.facility_fee > Decimal("0.0"), "Facility fee should be positive"
    assert breakdown.anesthesia_fee > Decimal("0.0"), "Anesthesia fee should be positive"
    assert breakdown.post_op_care > Decimal("0.0"), "Post-op care should be positive"
