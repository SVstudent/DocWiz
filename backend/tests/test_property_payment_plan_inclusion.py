"""Property-based tests for payment plan inclusion.

Feature: docwiz-surgical-platform, Property 12: Payment plan inclusion

For any completed cost calculation, the result should include at least one
payment plan option with monthly payment, duration, and interest rate.

Validates: Requirements 3.5
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
async def test_payment_plan_inclusion(
    procedure_id: str,
    patient_profile: PatientProfileResponse,
    mock_firestore,
):
    """
    Feature: docwiz-surgical-platform, Property 12: Payment plan inclusion
    
    For any completed cost calculation, the result should include at least one
    payment plan option with monthly payment, duration, and interest rate.
    
    Validates: Requirements 3.5
    """
    # Arrange - Create a fresh mock for each test
    mock_db = MagicMock()
    service = CostEstimationService(mock_db)
    
    # Act
    breakdown = await service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile,
    )
    
    # Assert - At least one payment plan must be present
    assert breakdown.payment_plans is not None, "Payment plans must be present"
    assert len(breakdown.payment_plans) > 0, "At least one payment plan must be included"
    
    # Check each payment plan has required fields
    for plan in breakdown.payment_plans:
        # Required fields must be present
        assert plan.name is not None, "Payment plan name must be present"
        assert plan.monthly_payment is not None, "Monthly payment must be present"
        assert plan.duration_months is not None, "Duration must be present"
        assert plan.interest_rate is not None, "Interest rate must be present"
        assert plan.total_paid is not None, "Total paid must be present"
        
        # Values must be valid
        assert plan.monthly_payment >= Decimal("0.0"), "Monthly payment must be non-negative"
        assert plan.duration_months > 0, "Duration must be positive"
        assert plan.interest_rate >= Decimal("0.0"), "Interest rate must be non-negative"
        assert plan.total_paid >= Decimal("0.0"), "Total paid must be non-negative"
        
        # Monthly payment * duration should approximately equal total paid
        expected_total = plan.monthly_payment * Decimal(str(plan.duration_months))
        # Allow for small rounding differences
        assert abs(expected_total - plan.total_paid) < Decimal("1.00"), (
            f"Monthly payment ({plan.monthly_payment}) * duration ({plan.duration_months}) "
            f"should approximately equal total paid ({plan.total_paid})"
        )
        
        # Total paid should equal patient responsibility (or more due to interest)
        # Allow for small rounding differences
        assert plan.total_paid >= breakdown.patient_responsibility - Decimal("0.01"), (
            f"Total paid ({plan.total_paid}) should be at least "
            f"patient responsibility ({breakdown.patient_responsibility})"
        )
