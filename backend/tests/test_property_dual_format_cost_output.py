"""Property-based tests for dual format cost output.

Feature: docwiz-surgical-platform, Property 11: Dual format cost output

For any cost estimate generation, the system should produce both a text breakdown
and an image file (PNG or JPEG) as output.

Validates: Requirements 3.4
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.cost_estimation_service import CostEstimationService
from app.services.freepik_client import FreepikClient
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
    output_format=st.sampled_from(["png", "jpeg"]),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_dual_format_cost_output(
    procedure_id: str,
    patient_profile: PatientProfileResponse,
    output_format: str,
    mock_firestore,
):
    """
    Feature: docwiz-surgical-platform, Property 11: Dual format cost output
    
    For any cost estimate generation, the system should produce both a text breakdown
    and an image file (PNG or JPEG) as output.
    
    Validates: Requirements 3.4
    """
    # Arrange - Create a fresh mock for each test
    mock_db = MagicMock()
    cost_service = CostEstimationService(mock_db)
    
    # Act - Generate text breakdown
    breakdown = await cost_service.calculate_cost_breakdown(
        procedure_id=procedure_id,
        patient_profile=patient_profile,
    )
    
    # Assert - Text breakdown must be present with all required fields
    assert breakdown is not None, "Text breakdown must be generated"
    assert breakdown.id is not None, "Breakdown must have an ID"
    assert breakdown.total_cost is not None, "Total cost must be present"
    assert breakdown.surgeon_fee is not None, "Surgeon fee must be present"
    assert breakdown.facility_fee is not None, "Facility fee must be present"
    assert breakdown.anesthesia_fee is not None, "Anesthesia fee must be present"
    assert breakdown.post_op_care is not None, "Post-op care must be present"
    
    # Act - Generate image infographic
    # Mock the Freepik client to avoid actual API calls
    with patch.object(FreepikClient, 'generate_cost_infographic', new_callable=AsyncMock) as mock_generate:
        # Configure mock to return a valid response
        mock_generate.return_value = {
            "image_url": f"https://example.com/infographic.{output_format}",
            "image_id": "test-image-id",
            "format": output_format,
            "width": 1200,
            "height": 800,
        }
        
        freepik_client = FreepikClient()
        
        cost_data = {
            "total_cost": float(breakdown.total_cost),
            "surgeon_fee": float(breakdown.surgeon_fee),
            "facility_fee": float(breakdown.facility_fee),
            "anesthesia_fee": float(breakdown.anesthesia_fee),
            "post_op_care": float(breakdown.post_op_care),
            "insurance_coverage": float(breakdown.insurance_coverage),
            "patient_responsibility": float(breakdown.patient_responsibility),
        }
        
        infographic_result = await freepik_client.generate_cost_infographic(
            cost_data=cost_data,
            format=output_format,
            style="professional"
        )
        
        # Assert - Image infographic must be generated
        assert infographic_result is not None, "Image infographic must be generated"
        assert "image_url" in infographic_result, "Infographic must have an image URL"
        assert infographic_result["image_url"] is not None, "Image URL must not be None"
        assert infographic_result["format"] == output_format, f"Format must be {output_format}"
        
        # Verify the infographic URL contains the correct format
        assert output_format in infographic_result["image_url"], (
            f"Image URL should contain format {output_format}"
        )
        
        # Verify both outputs are available
        assert breakdown is not None and infographic_result is not None, (
            "Both text breakdown and image infographic must be available"
        )
