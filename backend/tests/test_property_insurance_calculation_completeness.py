"""Property-based tests for insurance calculation completeness.

Feature: docwiz-surgical-platform, Property 10: Insurance calculation completeness

For any cost estimate with valid insurance information, the result should include
calculated values for coverage, deductible, copay, and out-of-pocket maximum.

Validates: Requirements 3.3
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
from app.db.seed_pricing import (
    PROCEDURE_BASE_PRICING,
    INSURANCE_PROVIDERS,
)


# Custom strategies
@st.composite
def patient_profile_with_insurance_strategy(draw):
    """Generate patient profile with valid insurance."""
    # Valid ZIP codes from different regions
    zip_codes = ["10001", "30301", "60601", "75201", "94101"]
    
    # Valid insurance providers (excluding "None")
    insurance_providers = [
        name for name in INSURANCE_PROVIDERS.keys()
        if name != "None"
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
    patient_profile=patient_profile_with_insurance_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_insurance_calculation_completeness(
    procedure_id: str,
    patient_profile: PatientProfileResponse,
    mock_firestore,
):
    """
    Feature: docwiz-surgical-platform, Property 10: Insurance calculation completeness
    
    For any cost estimate with valid insurance information, the result should include
    calculated values for coverage, deductible, copay, and out-of-pocket maximum.
    
    Validates: Requirements 3.3
    """
    # Arrange - Create a fresh mock for each test
    mock_db = MagicMock()
    service = CostEstimationService(mock_db)
    
    # Act
    breakdown = await service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile,
    )
    
    # Assert - All insurance-related fields must be present
    assert breakdown.insurance_coverage is not None, "Insurance coverage must be present"
    assert breakdown.deductible is not None, "Deductible must be present"
    assert breakdown.copay is not None, "Copay must be present"
    assert breakdown.out_of_pocket_max is not None, "Out-of-pocket maximum must be present"
    
    # All insurance fields should be non-negative
    assert breakdown.insurance_coverage >= Decimal("0.0"), "Insurance coverage must be non-negative"
    assert breakdown.deductible >= Decimal("0.0"), "Deductible must be non-negative"
    assert breakdown.copay >= Decimal("0.0"), "Copay must be non-negative"
    assert breakdown.out_of_pocket_max >= Decimal("0.0"), "Out-of-pocket max must be non-negative"
    
    # Patient responsibility should be present and non-negative
    assert breakdown.patient_responsibility is not None, "Patient responsibility must be present"
    assert breakdown.patient_responsibility >= Decimal("0.0"), "Patient responsibility must be non-negative"
    
    # Insurance provider should be recorded
    assert breakdown.insurance_provider is not None, "Insurance provider must be recorded"
    assert breakdown.insurance_provider == patient_profile.insurance_info.provider
    
    # The sum of insurance coverage and patient responsibility should equal total cost
    # (or patient responsibility should be capped at out-of-pocket max)
    total_paid = breakdown.insurance_coverage + breakdown.patient_responsibility
    
    # Allow for small rounding differences
    assert abs(total_paid - breakdown.total_cost) < Decimal("0.01"), (
        f"Insurance coverage ({breakdown.insurance_coverage}) + "
        f"patient responsibility ({breakdown.patient_responsibility}) "
        f"should equal total cost ({breakdown.total_cost})"
    )
    
    # Patient responsibility should not exceed out-of-pocket maximum
    assert breakdown.patient_responsibility <= breakdown.out_of_pocket_max, (
        f"Patient responsibility ({breakdown.patient_responsibility}) "
        f"should not exceed out-of-pocket max ({breakdown.out_of_pocket_max})"
    )
