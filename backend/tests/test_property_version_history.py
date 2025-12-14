"""Property-based tests for version history preservation.

Feature: docwiz-surgical-platform, Property 6: Version history preservation
Validates: Requirements 2.4
"""
import pytest
from datetime import date, datetime
from hypothesis import given, settings, strategies as st
from unittest.mock import AsyncMock, MagicMock, call

from app.schemas.profile import (
    InsuranceInfoCreate,
    LocationCreate,
    PatientProfileCreate,
    PatientProfileUpdate,
)
from app.services.profile_service import ProfileService
from app.db.firestore_models import PatientProfileModel, LocationModel, InsuranceInfoModel


# Custom strategies for profile updates
@st.composite
def profile_update_strategy(draw):
    """Generate valid profile update data."""
    # Randomly choose which fields to update
    update_name = draw(st.booleans())
    update_location = draw(st.booleans())
    
    updates = {}
    
    if update_name:
        updates['name'] = draw(st.text(min_size=1, max_size=100))
    
    if update_location:
        zip_code = draw(st.text(min_size=5, max_size=5, alphabet=st.characters(whitelist_categories=('Nd',))))
        updates['location'] = LocationCreate(
            zip_code=zip_code,
            city=draw(st.text(min_size=1, max_size=50)),
            state=draw(st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',)))),
            country="USA"
        )
    
    return PatientProfileUpdate(**updates)


@pytest.mark.property_test
@given(
    original_name=st.text(min_size=1, max_size=100),
    updated_name=st.text(min_size=1, max_size=100),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_version_history_preservation_on_update(original_name, updated_name):
    """
    Feature: docwiz-surgical-platform, Property 6: Version history preservation
    
    For any profile update operation, the system should increment the version number 
    and maintain a history record of the previous state.
    
    This test verifies that when a profile is updated, the version number increases
    and the previous state is saved to history.
    """
    # Skip if names are the same (no actual update)
    if original_name == updated_name:
        return
    
    # Create mock Firestore client
    mock_db = MagicMock()
    mock_profiles_collection = MagicMock()
    mock_history_collection = MagicMock()
    mock_profile_doc = MagicMock()
    mock_history_doc = MagicMock()
    
    # Setup collection routing
    def collection_router(name):
        if name == 'patient_profiles':
            return mock_profiles_collection
        elif name == 'profile_version_history':
            return mock_history_collection
        return MagicMock()
    
    mock_db.collection.side_effect = collection_router
    mock_profiles_collection.document.return_value = mock_profile_doc
    mock_history_collection.document.return_value = mock_history_doc
    
    # Create existing profile
    existing_profile = PatientProfileModel(
        id="profile-123",
        user_id="user-456",
        name=original_name,
        date_of_birth=datetime(1990, 1, 1),
        location=LocationModel(
            zip_code="12345",
            city="Test City",
            state="CA",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Blue Cross",
            encrypted_policy_number="encrypted-123",
        ),
        version=1
    )
    
    # Track the profile state across get calls
    profile_state = [existing_profile.model_dump(mode='json')]
    
    def get_side_effect():
        mock_get = MagicMock()
        mock_get.exists = True
        mock_get.to_dict.return_value = profile_state[0]
        return mock_get
    
    mock_profile_doc.get.side_effect = get_side_effect
    
    # Mock update to modify the profile state
    def update_side_effect(data):
        # Update the profile state with new data
        profile_state[0].update(data)
    
    mock_profile_doc.update.side_effect = update_side_effect
    
    # Create profile service
    profile_service = ProfileService(mock_db)
    
    # Update profile
    updates = PatientProfileUpdate(name=updated_name)
    updated_profile = await profile_service.update_profile("profile-123", updates)
    
    # Verify version was incremented
    assert updated_profile.version == 2, "Version should be incremented from 1 to 2"
    
    # Verify history was saved (check that history collection was accessed)
    history_calls = [call for call in mock_db.collection.call_args_list if call[0][0] == 'profile_version_history']
    assert len(history_calls) > 0, "Version history should be saved"
    
    # Verify history document was created
    mock_history_doc.set.assert_called_once()
    history_data = mock_history_doc.set.call_args[0][0]
    assert history_data['profile_id'] == "profile-123", "History should reference correct profile"
    assert history_data['version'] == 1, "History should store previous version number"


@pytest.mark.property_test
@given(
    num_updates=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_version_increments_with_each_update(num_updates):
    """
    Feature: docwiz-surgical-platform, Property 6: Version history preservation
    
    For any sequence of profile updates, the version number should increment 
    with each update, and each previous state should be preserved in history.
    
    This test verifies that multiple updates result in monotonically increasing
    version numbers.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    mock_profiles_collection = MagicMock()
    mock_history_collection = MagicMock()
    mock_profile_doc = MagicMock()
    mock_history_doc = MagicMock()
    
    # Setup collection routing
    def collection_router(name):
        if name == 'patient_profiles':
            return mock_profiles_collection
        elif name == 'profile_version_history':
            return mock_history_collection
        return MagicMock()
    
    mock_db.collection.side_effect = collection_router
    mock_profiles_collection.document.return_value = mock_profile_doc
    mock_history_collection.document.return_value = mock_history_doc
    
    # Track version across updates
    current_version = 1
    
    # Create initial profile
    profile = PatientProfileModel(
        id="profile-123",
        user_id="user-456",
        name="Original Name",
        date_of_birth=datetime(1990, 1, 1),
        location=LocationModel(
            zip_code="12345",
            city="Test City",
            state="CA",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Blue Cross",
            encrypted_policy_number="encrypted-123",
        ),
        version=current_version
    )
    
    # Create profile service
    profile_service = ProfileService(mock_db)
    
    # Track the profile state across get calls
    profile_state = [profile.model_dump(mode='json')]
    
    def get_side_effect():
        mock_get = MagicMock()
        mock_get.exists = True
        mock_get.to_dict.return_value = profile_state[0].copy()
        return mock_get
    
    mock_profile_doc.get.side_effect = get_side_effect
    
    # Mock update to modify the profile state
    def update_side_effect(data):
        profile_state[0].update(data)
    
    mock_profile_doc.update.side_effect = update_side_effect
    
    # Perform multiple updates
    for i in range(num_updates):
        # Update profile with new name
        updates = PatientProfileUpdate(name=f"Updated Name {i+1}")
        updated_profile = await profile_service.update_profile("profile-123", updates)
        
        # Verify version incremented
        expected_version = current_version + 1
        assert updated_profile.version == expected_version, f"Version should increment to {expected_version}"
        
        # Update for next iteration
        current_version = updated_profile.version
        profile = updated_profile
    
    # Verify final version is correct
    assert profile.version == num_updates + 1, f"Final version should be {num_updates + 1}"


@pytest.mark.property_test
@given(
    original_data=st.text(min_size=1, max_size=100),
    updated_data=st.text(min_size=1, max_size=100),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_history_preserves_previous_state(original_data, updated_data):
    """
    Feature: docwiz-surgical-platform, Property 6: Version history preservation
    
    For any profile update operation, the history record should contain the 
    complete previous state of the profile before the update.
    
    This test verifies that the history record accurately captures the state
    before modification.
    """
    # Skip if data is the same
    if original_data == updated_data:
        return
    
    # Create mock Firestore client
    mock_db = MagicMock()
    mock_profiles_collection = MagicMock()
    mock_history_collection = MagicMock()
    mock_profile_doc = MagicMock()
    mock_history_doc = MagicMock()
    
    # Setup collection routing
    def collection_router(name):
        if name == 'patient_profiles':
            return mock_profiles_collection
        elif name == 'profile_version_history':
            return mock_history_collection
        return MagicMock()
    
    mock_db.collection.side_effect = collection_router
    mock_profiles_collection.document.return_value = mock_profile_doc
    mock_history_collection.document.return_value = mock_history_doc
    
    # Create existing profile with original data
    existing_profile = PatientProfileModel(
        id="profile-123",
        user_id="user-456",
        name=original_data,
        date_of_birth=datetime(1990, 1, 1),
        location=LocationModel(
            zip_code="12345",
            city="Test City",
            state="CA",
            country="USA"
        ),
        insurance_info=InsuranceInfoModel(
            provider="Blue Cross",
            encrypted_policy_number="encrypted-123",
        ),
        version=1
    )
    
    # Track the profile state
    profile_state = [existing_profile.model_dump(mode='json')]
    
    def get_side_effect():
        mock_get = MagicMock()
        mock_get.exists = True
        mock_get.to_dict.return_value = profile_state[0].copy()
        return mock_get
    
    mock_profile_doc.get.side_effect = get_side_effect
    
    # Mock update to modify the profile state
    def update_side_effect(data):
        profile_state[0].update(data)
    
    mock_profile_doc.update.side_effect = update_side_effect
    
    # Create profile service
    profile_service = ProfileService(mock_db)
    
    # Update profile
    updates = PatientProfileUpdate(name=updated_data)
    await profile_service.update_profile("profile-123", updates)
    
    # Verify history was saved with original data
    mock_history_doc.set.assert_called_once()
    history_data = mock_history_doc.set.call_args[0][0]
    
    # The history should contain the original name
    assert history_data['data']['name'] == original_data, "History should preserve original name"
    assert history_data['version'] == 1, "History should record the version being saved"
