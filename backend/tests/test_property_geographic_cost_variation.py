"""Property-based tests for geographic cost variation.

Feature: docwiz-surgical-platform, Property 9: Geographic cost variation

For any procedure, calculating costs for two different geographic locations
should produce different total costs (unless locations have identical pricing).

Validates: Requirements 3.2
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
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
    get_region_from_zip,
    get_regional_multiplier,
)


# Custom strategies
@st.composite
def patient_profile_with_zip_strategy(draw, zip_code: str):
    """Generate patient profile with specific ZIP code."""
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
            zip_code=zip_code,
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
    zip_code_1=st.sampled_from(["10001", "30301", "60601", "75201", "94101"]),
    zip_code_2=st.sampled_from(["10001", "30301", "60601", "75201", "94101"]),
    data=st.data(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_geographic_cost_variation(
    procedure_id: str,
    zip_code_1: str,
    zip_code_2: str,
    data,
    mock_firestore,
):
    """
    Feature: docwiz-surgical-platform, Property 9: Geographic cost variation
    
    For any procedure, calculating costs for two different geographic locations
    should produce different total costs (unless locations have identical pricing).
    
    Validates: Requirements 3.2
    """
    # Assume the ZIP codes are in different regions
    region_1 = get_region_from_zip(zip_code_1)
    region_2 = get_region_from_zip(zip_code_2)
    
    # Only test when regions are different (otherwise costs should be the same)
    assume(region_1 != region_2)
    
    # Arrange - Create a fresh mock for each test
    mock_db = MagicMock()
    service = CostEstimationService(mock_db)
    
    # Generate patient profiles with different ZIP codes
    patient_profile_1 = data.draw(patient_profile_with_zip_strategy(zip_code_1))
    patient_profile_2 = data.draw(patient_profile_with_zip_strategy(zip_code_2))
    
    # Act - Calculate costs for both locations
    breakdown_1 = await service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile_1,
    )
    
    breakdown_2 = await service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile_2,
    )
    
    # Assert - Costs should be different for different regions
    # (unless the regional multipliers happen to be the same, which they're not in our data)
    multiplier_1 = get_regional_multiplier(region_1)
    multiplier_2 = get_regional_multiplier(region_2)
    
    if multiplier_1 != multiplier_2:
        # Total costs should be different
        assert breakdown_1.total_cost != breakdown_2.total_cost, (
            f"Costs should differ for different regions: "
            f"{region_1} (${breakdown_1.total_cost}) vs "
            f"{region_2} (${breakdown_2.total_cost})"
        )
        
        # Individual components should also differ
        assert breakdown_1.surgeon_fee != breakdown_2.surgeon_fee
        assert breakdown_1.facility_fee != breakdown_2.facility_fee
        assert breakdown_1.anesthesia_fee != breakdown_2.anesthesia_fee
        assert breakdown_1.post_op_care != breakdown_2.post_op_care
        
        # The ratio of costs should match the ratio of multipliers
        cost_ratio = breakdown_1.total_cost / breakdown_2.total_cost
        multiplier_ratio = multiplier_1 / multiplier_2
        
        # Allow for small rounding differences
        assert abs(cost_ratio - multiplier_ratio) < Decimal("0.01"), (
            f"Cost ratio {cost_ratio} should match multiplier ratio {multiplier_ratio}"
        )
    else:
        # If multipliers are the same, costs should be the same
        assert breakdown_1.total_cost == breakdown_2.total_cost
