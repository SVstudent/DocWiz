"""Property-based tests for cost estimate transparency.

Feature: docwiz-surgical-platform, Property 21: Cost estimate transparency

For any cost estimate, the output should include citations of data sources
and documentation of calculation methods used.

Validates: Requirements 6.4
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
async def test_cost_estimate_transparency(
    procedure_id: str,
    patient_profile: PatientProfileResponse,
    mock_firestore,
):
    """
    Feature: docwiz-surgical-platform, Property 21: Cost estimate transparency
    
    For any cost estimate, the output should include citations of data sources
    and documentation of calculation methods used.
    
    Validates: Requirements 6.4
    """
    # Arrange - Create a fresh mock for each test
    mock_db = MagicMock()
    service = CostEstimationService(mock_db)
    
    # Act
    breakdown = await service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile,
    )
    
    # Assert - Data sources must be present and documented
    assert breakdown.data_sources is not None, "Data sources must be present"
    assert len(breakdown.data_sources) > 0, "At least one data source must be cited"
    
    # Each data source should be a non-empty string
    for source in breakdown.data_sources:
        assert isinstance(source, str), "Data source must be a string"
        assert len(source) > 0, "Data source must not be empty"
    
    # Data sources should include information about calculation methods
    data_sources_text = " ".join(breakdown.data_sources).lower()
    
    # Should mention cost data source
    assert any(keyword in data_sources_text for keyword in ["cost", "average", "pricing"]), (
        "Data sources should mention cost data"
    )
    
    # Should mention regional adjustment if applicable
    assert "region" in data_sources_text, (
        "Data sources should document regional cost adjustment"
    )
    
    # Region should be documented
    assert breakdown.region is not None, "Region must be documented"
    assert len(breakdown.region) > 0, "Region must not be empty"
    
    # If insurance is used, it should be documented in data sources
    if breakdown.insurance_provider and breakdown.insurance_provider != "None":
        # Check if insurance provider is mentioned in data sources
        insurance_mentioned = any(
            breakdown.insurance_provider.lower() in source.lower()
            for source in breakdown.data_sources
        )
        assert insurance_mentioned, (
            f"Insurance provider {breakdown.insurance_provider} should be cited in data sources"
        )
    
    # Calculation method should be transparent through the breakdown structure
    # All cost components should be present and sum to total
    calculated_total = (
        breakdown.surgeon_fee +
        breakdown.facility_fee +
        breakdown.anesthesia_fee +
        breakdown.post_op_care
    )
    assert breakdown.total_cost == calculated_total, (
        "Total cost calculation method should be transparent (sum of components)"
    )
    
    # Insurance calculation should be transparent
    calculated_patient_total = breakdown.insurance_coverage + breakdown.patient_responsibility
    # Allow for small rounding differences
    assert abs(calculated_patient_total - breakdown.total_cost) < Decimal("0.01"), (
        "Insurance calculation method should be transparent "
        "(coverage + patient responsibility = total cost)"
    )
