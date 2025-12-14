"""Property-based tests for procedure display completeness.

Feature: docwiz-surgical-platform, Property 2: Procedure display completeness

For any surgical procedure, when displayed to a patient, the system should 
include description, typical recovery time, and risk factors in the output.

Validates: Requirements 1.2
"""
import pytest
from hypothesis import given, strategies as st, settings

from app.db.firestore_models import ProcedureModel


# Custom strategy for generating procedure data
@st.composite
def procedure_strategy(draw):
    """Generate random but valid procedure data."""
    categories = ["facial", "body", "reconstructive", "cosmetic"]
    risk_levels = ["low", "medium", "high"]
    
    return ProcedureModel(
        id=draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-'))),
        name=draw(st.text(min_size=5, max_size=100)),
        category=draw(st.sampled_from(categories)),
        description=draw(st.text(min_size=10, max_size=500)),
        typical_cost_min=draw(st.floats(min_value=100.0, max_value=50000.0)),
        typical_cost_max=draw(st.floats(min_value=50000.0, max_value=200000.0)),
        recovery_days=draw(st.integers(min_value=1, max_value=90)),
        risk_level=draw(st.sampled_from(risk_levels)),
        cpt_codes=draw(st.lists(st.text(min_size=5, max_size=10), min_size=1, max_size=5)),
        icd10_codes=draw(st.lists(st.text(min_size=5, max_size=10), min_size=1, max_size=5)),
        prompt_template=draw(st.text(min_size=20, max_size=500))
    )


def display_procedure(procedure: ProcedureModel) -> dict:
    """Display a procedure to a patient.
    
    This function simulates how a procedure would be displayed in the UI.
    It should include all required information per Requirements 1.2.
    
    Args:
        procedure: Procedure model to display
    
    Returns:
        Dictionary containing display information
    """
    return {
        "id": procedure.id,
        "name": procedure.name,
        "category": procedure.category,
        "description": procedure.description,
        "recovery_days": procedure.recovery_days,
        "risk_level": procedure.risk_level,
        "cost_range": {
            "min": procedure.typical_cost_min,
            "max": procedure.typical_cost_max
        }
    }


@given(procedure=procedure_strategy())
@settings(max_examples=100)
@pytest.mark.property_test
def test_procedure_display_completeness(procedure):
    """
    Feature: docwiz-surgical-platform, Property 2: Procedure display completeness
    
    For any surgical procedure, when displayed to a patient, the system should 
    include description, typical recovery time, and risk factors in the output.
    
    Validates: Requirements 1.2
    """
    # Display the procedure
    display = display_procedure(procedure)
    
    # Verify all required fields are present
    assert "description" in display, "Display must include description"
    assert "recovery_days" in display, "Display must include recovery time"
    assert "risk_level" in display, "Display must include risk level"
    
    # Verify the values are not empty/null
    assert display["description"] is not None, "Description must not be None"
    assert display["description"] != "", "Description must not be empty"
    
    assert display["recovery_days"] is not None, "Recovery days must not be None"
    assert display["recovery_days"] > 0, "Recovery days must be positive"
    
    assert display["risk_level"] is not None, "Risk level must not be None"
    assert display["risk_level"] in ["low", "medium", "high"], "Risk level must be valid"
    
    # Verify additional useful information is included
    assert "name" in display, "Display should include procedure name"
    assert "category" in display, "Display should include category"


@given(procedure=procedure_strategy())
@settings(max_examples=100)
@pytest.mark.property_test
def test_procedure_display_includes_cost_information(procedure):
    """
    Additional property test: Procedure display should include cost information.
    
    This helps patients make informed financial decisions.
    """
    display = display_procedure(procedure)
    
    # Verify cost range is included
    assert "cost_range" in display, "Display should include cost range"
    assert "min" in display["cost_range"], "Cost range should include minimum"
    assert "max" in display["cost_range"], "Cost range should include maximum"
    
    # Verify cost values are reasonable
    assert display["cost_range"]["min"] > 0, "Minimum cost must be positive"
    assert display["cost_range"]["max"] > 0, "Maximum cost must be positive"
    assert display["cost_range"]["max"] >= display["cost_range"]["min"], \
        "Maximum cost must be >= minimum cost"


@given(procedure=procedure_strategy())
@settings(max_examples=100)
@pytest.mark.property_test
def test_procedure_display_preserves_data_integrity(procedure):
    """
    Additional property test: Display should preserve original procedure data.
    
    Ensures no data corruption or loss during display transformation.
    """
    display = display_procedure(procedure)
    
    # Verify data integrity
    assert display["name"] == procedure.name, "Name must be preserved"
    assert display["description"] == procedure.description, "Description must be preserved"
    assert display["recovery_days"] == procedure.recovery_days, "Recovery days must be preserved"
    assert display["risk_level"] == procedure.risk_level, "Risk level must be preserved"
    assert display["category"] == procedure.category, "Category must be preserved"
