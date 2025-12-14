"""Property-based tests for profile field completeness.

Feature: docwiz-surgical-platform, Property 3: Profile field completeness
Validates: Requirements 2.1
"""
import pytest
from datetime import date, datetime
from hypothesis import given, settings, strategies as st
from unittest.mock import AsyncMock, MagicMock

from app.schemas.profile import (
    InsuranceInfoCreate,
    LocationCreate,
    PatientProfileCreate,
)
from app.services.profile_service import ProfileService


# Custom strategies for profile data
@st.composite
def location_strategy(draw):
    """Generate valid location data."""
    # Generate 5-digit zip code
    zip_code = draw(st.text(min_size=5, max_size=5, alphabet=st.characters(whitelist_categories=('Nd',))))
    city = draw(st.text(min_size=1, max_size=50))
    state = draw(st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',))))
    
    return LocationCreate(
        zip_code=zip_code,
        city=city,
        state=state,
        country="USA"
    )


@st.composite
def insurance_info_strategy(draw):
    """Generate valid insurance info data."""
    provider = draw(st.sampled_from([
        'Blue Cross Blue Shield',
        'Aetna',
        'UnitedHealthcare',
        'Cigna',
        'Humana',
    ]))
    policy_number = draw(st.text(min_size=5, max_size=20))
    group_number = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    plan_type = draw(st.one_of(st.none(), st.sampled_from(['HMO', 'PPO', 'EPO', 'POS'])))
    
    return InsuranceInfoCreate(
        provider=provider,
        policy_number=policy_number,
        group_number=group_number,
        plan_type=plan_type
    )


@st.composite
def patient_profile_strategy(draw):
    """Generate valid patient profile data."""
    name = draw(st.text(min_size=1, max_size=100))
    # Generate date between 1920 and 2020
    year = draw(st.integers(min_value=1920, max_value=2020))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Use 28 to avoid invalid dates
    date_of_birth = date(year, month, day)
    
    location = draw(location_strategy())
    insurance_info = draw(insurance_info_strategy())
    medical_history = draw(st.one_of(st.none(), st.text(min_size=0, max_size=500)))
    
    return PatientProfileCreate(
        name=name,
        date_of_birth=date_of_birth,
        location=location,
        insurance_info=insurance_info,
        medical_history=medical_history
    )


@pytest.mark.property_test
@given(profile_data=patient_profile_strategy())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_profile_field_completeness(profile_data):
    """
    Feature: docwiz-surgical-platform, Property 3: Profile field completeness
    
    For any patient profile creation, the system should require and store name, 
    date of birth, insurance provider, policy number, and location.
    
    This test verifies that when a profile is created with all required fields,
    the stored profile contains all those fields.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    # Create profile service
    profile_service = ProfileService(mock_db)
    
    # Create profile
    user_id = "test-user-123"
    profile = await profile_service.create_profile(user_id, profile_data)
    
    # Verify all required fields are present in the created profile
    assert profile.name == profile_data.name, "Name should be stored"
    assert profile.date_of_birth is not None, "Date of birth should be stored"
    assert profile.location is not None, "Location should be stored"
    assert profile.location.zip_code == profile_data.location.zip_code, "Zip code should be stored"
    assert profile.insurance_info is not None, "Insurance info should be stored"
    assert profile.insurance_info.provider == profile_data.insurance_info.provider, "Insurance provider should be stored"
    assert profile.insurance_info.encrypted_policy_number is not None, "Policy number should be stored (encrypted)"
    assert profile.user_id == user_id, "User ID should be stored"
    
    # Verify the profile was saved to Firestore
    mock_db.collection.assert_called_with('patient_profiles')
    mock_collection.document.assert_called_once()
    mock_document.set.assert_called_once()


@pytest.mark.property_test
@given(
    name=st.text(min_size=1, max_size=100),
    policy_number=st.text(min_size=5, max_size=20),
    zip_code=st.text(min_size=5, max_size=5, alphabet=st.characters(whitelist_categories=('Nd',))),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_required_fields_always_stored(name, policy_number, zip_code):
    """
    Feature: docwiz-surgical-platform, Property 3: Profile field completeness
    
    For any patient profile creation, the system should require and store name, 
    date of birth, insurance provider, policy number, and location.
    
    This test verifies that the five required fields (name, date_of_birth, 
    insurance provider, policy number, location) are always present in the 
    stored profile, regardless of input variations.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    # Create profile service
    profile_service = ProfileService(mock_db)
    
    # Create minimal profile with required fields
    profile_data = PatientProfileCreate(
        name=name,
        date_of_birth=date(1990, 1, 1),
        location=LocationCreate(
            zip_code=zip_code,
            city="Test City",
            state="CA",
            country="USA"
        ),
        insurance_info=InsuranceInfoCreate(
            provider="Blue Cross Blue Shield",
            policy_number=policy_number
        )
    )
    
    # Create profile
    user_id = "test-user-456"
    profile = await profile_service.create_profile(user_id, profile_data)
    
    # Verify all 5 required fields are present
    assert profile.name is not None and profile.name != "", "Name must be stored"
    assert profile.date_of_birth is not None, "Date of birth must be stored"
    assert profile.insurance_info is not None, "Insurance info must be stored"
    assert profile.insurance_info.provider is not None and profile.insurance_info.provider != "", "Insurance provider must be stored"
    assert profile.insurance_info.encrypted_policy_number is not None and profile.insurance_info.encrypted_policy_number != "", "Policy number must be stored"
    assert profile.location is not None, "Location must be stored"
    assert profile.location.zip_code is not None and profile.location.zip_code != "", "Location (zip code) must be stored"


@pytest.mark.property_test
@given(profile_data=patient_profile_strategy())
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_profile_contains_user_id(profile_data):
    """
    Feature: docwiz-surgical-platform, Property 3: Profile field completeness
    
    For any patient profile creation, the system should store the user_id 
    to associate the profile with the user who created it.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    
    # Create profile service
    profile_service = ProfileService(mock_db)
    
    # Create profile with random user ID
    user_id = f"user-{hash(profile_data.name) % 10000}"
    profile = await profile_service.create_profile(user_id, profile_data)
    
    # Verify user_id is stored and matches
    assert profile.user_id == user_id, "User ID must be stored and match the creating user"
