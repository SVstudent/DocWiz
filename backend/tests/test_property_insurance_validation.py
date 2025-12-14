"""Property-based tests for insurance validation.

Feature: docwiz-surgical-platform, Property 4: Insurance validation
Validates: Requirements 2.2
"""
import pytest
from hypothesis import given, settings, strategies as st
from unittest.mock import MagicMock

from app.services.profile_service import ProfileService


# List of supported providers (matching the service implementation)
SUPPORTED_PROVIDERS = [
    'Blue Cross Blue Shield',
    'Aetna',
    'UnitedHealthcare',
    'Cigna',
    'Humana',
    'Kaiser Permanente',
    'Anthem',
    'Medicare',
    'Medicaid',
]


@pytest.mark.property_test
@given(
    provider=st.sampled_from(SUPPORTED_PROVIDERS)
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_supported_providers_validate(provider):
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any insurance provider input, the validation function should return true 
    for providers in the supported database and false for all others.
    
    This test verifies that all supported providers are correctly validated.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Validate provider
    is_valid = await profile_service.validate_insurance_provider(provider)
    
    # Should be valid
    assert is_valid == True, f"Supported provider '{provider}' should be valid"


@pytest.mark.property_test
@given(
    provider=st.text(min_size=1, max_size=50, alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),  # Exclude control characters
        blacklist_characters=list(SUPPORTED_PROVIDERS[0])  # Exclude chars from first provider to reduce matches
    ))
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_unsupported_providers_rejected(provider):
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any insurance provider input, the validation function should return true 
    for providers in the supported database and false for all others.
    
    This test verifies that unsupported providers are correctly rejected.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Validate provider
    is_valid = await profile_service.validate_insurance_provider(provider)
    
    # Check if provider matches any supported provider (case-insensitive partial match)
    provider_lower = provider.lower()
    matches_supported = any(
        provider_lower in supported.lower() or supported.lower() in provider_lower
        for supported in SUPPORTED_PROVIDERS
    )
    
    # Validation result should match our expectation
    if matches_supported:
        assert is_valid == True, f"Provider '{provider}' matches supported provider and should be valid"
    else:
        assert is_valid == False, f"Unsupported provider '{provider}' should be invalid"


@pytest.mark.property_test
@given(
    provider=st.sampled_from(SUPPORTED_PROVIDERS),
    case_transform=st.sampled_from(['upper', 'lower', 'title', 'mixed'])
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_case_insensitive_validation(provider, case_transform):
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any insurance provider input, the validation should be case-insensitive,
    accepting providers regardless of capitalization.
    
    This test verifies that validation works with different case transformations.
    """
    # Transform the provider name
    if case_transform == 'upper':
        transformed = provider.upper()
    elif case_transform == 'lower':
        transformed = provider.lower()
    elif case_transform == 'title':
        transformed = provider.title()
    else:  # mixed
        transformed = ''.join(
            c.upper() if i % 2 == 0 else c.lower()
            for i, c in enumerate(provider)
        )
    
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Validate transformed provider
    is_valid = await profile_service.validate_insurance_provider(transformed)
    
    # Should be valid regardless of case
    assert is_valid == True, f"Provider '{transformed}' (from '{provider}') should be valid regardless of case"


@pytest.mark.property_test
@given(
    provider=st.sampled_from(SUPPORTED_PROVIDERS),
    prefix=st.text(min_size=0, max_size=10),
    suffix=st.text(min_size=0, max_size=10)
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_partial_match_validation(provider, prefix, suffix):
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any insurance provider input, the validation should support partial matching,
    accepting providers that contain or are contained in supported provider names.
    
    This test verifies that partial matching works correctly.
    """
    # Create a string with the provider name embedded
    test_string = f"{prefix}{provider}{suffix}"
    
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Validate the string
    is_valid = await profile_service.validate_insurance_provider(test_string)
    
    # Should be valid if the provider name is contained in the test string
    # (which it always is in this test)
    assert is_valid == True, f"String '{test_string}' containing provider '{provider}' should be valid"


@pytest.mark.property_test
@given(
    provider=st.sampled_from(['Blue Cross', 'BCBS', 'Blue Shield', 'Aetna Inc', 'United Healthcare'])
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_common_abbreviations_and_variations(provider):
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any insurance provider input, the validation should accept common 
    abbreviations and variations of supported provider names.
    
    This test verifies that common variations are correctly validated.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Validate provider
    is_valid = await profile_service.validate_insurance_provider(provider)
    
    # These are all variations of supported providers and should be valid
    assert is_valid == True, f"Common variation '{provider}' should be valid"


@pytest.mark.property_test
@given(
    provider=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),  # Letters and digits only
            min_codepoint=65,  # Start from 'A'
            max_codepoint=122  # End at 'z'
        )
    )
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_validation_consistency(provider):
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any insurance provider input, the validation function should return 
    consistent results when called multiple times with the same input.
    
    This test verifies that validation is deterministic.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Validate provider multiple times
    result1 = await profile_service.validate_insurance_provider(provider)
    result2 = await profile_service.validate_insurance_provider(provider)
    result3 = await profile_service.validate_insurance_provider(provider)
    
    # Results should be consistent
    assert result1 == result2 == result3, \
        f"Validation of '{provider}' should return consistent results"


@pytest.mark.property_test
@pytest.mark.asyncio
async def test_empty_provider_rejected():
    """
    Feature: docwiz-surgical-platform, Property 4: Insurance validation
    
    For any empty or whitespace-only insurance provider input, the validation 
    function should return false.
    
    This test verifies that empty providers are rejected.
    """
    # Create mock Firestore client
    mock_db = MagicMock()
    profile_service = ProfileService(mock_db)
    
    # Test empty string
    is_valid_empty = await profile_service.validate_insurance_provider("")
    assert is_valid_empty == False, "Empty provider should be invalid"
    
    # Test whitespace-only string
    is_valid_whitespace = await profile_service.validate_insurance_provider("   ")
    assert is_valid_whitespace == False, "Whitespace-only provider should be invalid"
