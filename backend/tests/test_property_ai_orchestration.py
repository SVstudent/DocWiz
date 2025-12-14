"""Property-based tests for AI service orchestration.

Feature: docwiz-surgical-platform, Property 27: AI service orchestration
Validates: Requirements 9.2
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from hypothesis import given, settings, strategies as st, HealthCheck

from app.services.gemini_client import GeminiClient, GeminiAPIError
from app.services.nano_banana_client import NanoBananaClient, NanoBananaAPIError


# Strategy for generating valid image data (small test images)
@st.composite
def image_data_strategy(draw):
    """Generate valid image data for testing."""
    # Generate small random image data (simulating JPEG header + data)
    size = draw(st.integers(min_value=1024, max_value=10240))
    return b'\xff\xd8\xff\xe0' + b'\x00' * (size - 4)  # JPEG header + padding


# Strategy for generating surgical prompts
@st.composite
def surgical_prompt_strategy(draw):
    """Generate surgical modification prompts."""
    procedures = [
        "rhinoplasty with subtle nasal bridge refinement",
        "breast augmentation with natural appearance",
        "cleft lip repair with symmetrical results",
        "facelift with natural skin tightening",
        "blepharoplasty with eyelid rejuvenation"
    ]
    procedure = draw(st.sampled_from(procedures))
    return f"Apply {procedure} to this patient photo, maintaining natural appearance and facial features"


# Strategy for generating procedure information
@st.composite
def procedure_info_strategy(draw):
    """Generate procedure information for medical justification."""
    procedures = [
        ("Rhinoplasty", "Surgical reshaping of the nose"),
        ("Breast Augmentation", "Surgical enhancement of breast size"),
        ("Cleft Lip Repair", "Surgical correction of cleft lip deformity"),
        ("Facelift", "Surgical facial rejuvenation procedure"),
        ("Blepharoplasty", "Surgical eyelid rejuvenation")
    ]
    name, description = draw(st.sampled_from(procedures))
    return {
        "name": name,
        "description": description,
        "cpt_codes": draw(st.lists(st.text(min_size=5, max_size=5), min_size=1, max_size=3)),
        "icd10_codes": draw(st.lists(st.text(min_size=3, max_size=7), min_size=1, max_size=3))
    }


@pytest.mark.property_test
@given(
    image_data=image_data_strategy(),
    prompt=surgical_prompt_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_gemini_api_called_for_visualization(image_data, prompt):
    """
    Feature: docwiz-surgical-platform, Property 27: AI service orchestration
    
    For any surgical visualization request, the system should make calls to 
    Gemini 2.5 Flash Image API and record the interaction.
    
    This test verifies that Gemini API is called when generating visualizations.
    """
    # Mock the HTTP client to avoid actual API calls
    mock_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Generated surgical preview description"
                        }
                    ]
                },
                "finishReason": "STOP",
                "safetyRatings": []
            }
        ]
    }
    
    with patch('httpx.AsyncClient') as mock_client_class:
        # Setup mock
        mock_client = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_client.post.return_value = mock_response_obj
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Create client and make request
        client = GeminiClient(api_key="test-key")
        result = await client.generate_image(image_data, prompt)
        
        # Verify Gemini API was called
        assert mock_client.post.called, "Gemini API should be called for visualization"
        
        # Verify the call was made to the correct endpoint
        call_args = mock_client.post.call_args
        assert "generateContent" in call_args[0][0], "Should call generateContent endpoint"
        
        # Verify result contains expected fields
        assert "content" in result, "Result should contain content"
        assert "finish_reason" in result, "Result should contain finish_reason"


@pytest.mark.property_test
@given(
    procedure_info=procedure_info_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_nano_banana_api_called_for_justification(procedure_info):
    """
    Feature: docwiz-surgical-platform, Property 27: AI service orchestration
    
    For any medical justification request, the system should make calls to 
    Nano Banana API and record the interaction.
    
    This test verifies that Nano Banana API is called when generating medical justifications.
    """
    # Mock the HTTP client to avoid actual API calls
    mock_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Medical necessity justification for the procedure..."
                        }
                    ]
                },
                "finishReason": "STOP",
                "safetyRatings": []
            }
        ]
    }
    
    with patch('httpx.AsyncClient') as mock_client_class:
        # Setup mock
        mock_client = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_client.post.return_value = mock_response_obj
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Create client and make request
        client = NanoBananaClient(api_key="test-key")
        result = await client.generate_medical_justification(
            procedure_name=procedure_info["name"],
            procedure_description=procedure_info["description"],
            cpt_codes=procedure_info["cpt_codes"],
            icd10_codes=procedure_info["icd10_codes"]
        )
        
        # Verify Nano Banana API was called
        assert mock_client.post.called, "Nano Banana API should be called for justification"
        
        # Verify the call was made to the correct endpoint
        call_args = mock_client.post.call_args
        assert "generateContent" in call_args[0][0], "Should call generateContent endpoint"
        
        # Verify result is a string (the justification text)
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Result should not be empty"


@pytest.mark.property_test
@given(
    image_data=image_data_strategy(),
    prompt=surgical_prompt_strategy(),
    max_retries=st.integers(min_value=1, max_value=3),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_gemini_retry_logic_on_failure(image_data, prompt, max_retries):
    """
    Feature: docwiz-surgical-platform, Property 27: AI service orchestration
    
    For any API request that fails, the system should implement retry logic
    with exponential backoff.
    
    This test verifies that retry logic is properly implemented.
    """
    with patch('httpx.AsyncClient') as mock_client_class:
        # Setup mock to fail initially then succeed
        mock_client = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 500
        mock_response_obj.text = "Internal Server Error"
        mock_client.post.return_value = mock_response_obj
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Create client with specific max_retries
        client = GeminiClient(api_key="test-key")
        client.max_retries = max_retries
        
        # Attempt to generate image (should fail and retry)
        with pytest.raises(GeminiAPIError):
            await client.generate_image(image_data, prompt)
        
        # Verify retry attempts were made
        assert mock_client.post.call_count == max_retries, (
            f"Should retry {max_retries} times on failure"
        )


@pytest.mark.property_test
@given(
    procedure_info=procedure_info_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_nano_banana_error_handling(procedure_info):
    """
    Feature: docwiz-surgical-platform, Property 27: AI service orchestration
    
    For any API request that encounters an error, the system should handle
    errors gracefully and raise appropriate exceptions.
    
    This test verifies proper error handling for Nano Banana API.
    """
    with patch('httpx.AsyncClient') as mock_client_class:
        # Setup mock to return error
        mock_client = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 400
        mock_response_obj.text = "Bad Request"
        mock_client.post.return_value = mock_response_obj
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Create client
        client = NanoBananaClient(api_key="test-key")
        
        # Attempt to generate justification (should raise error)
        with pytest.raises(NanoBananaAPIError):
            await client.generate_medical_justification(
                procedure_name=procedure_info["name"],
                procedure_description=procedure_info["description"]
            )


@pytest.mark.property_test
@given(
    api_key=st.text(min_size=10, max_size=50),
)
@settings(
    max_examples=100,
    deadline=None,
)
def test_ai_clients_initialization(api_key):
    """
    Feature: docwiz-surgical-platform, Property 27: AI service orchestration
    
    For any valid API key, the AI service clients should initialize properly
    and store the API key for subsequent requests.
    
    This test verifies proper client initialization.
    """
    # Test Gemini client initialization
    gemini_client = GeminiClient(api_key=api_key)
    assert gemini_client.api_key == api_key, "Gemini client should store API key"
    assert gemini_client.max_retries > 0, "Should have retry configuration"
    
    # Test Nano Banana client initialization
    nano_client = NanoBananaClient(api_key=api_key)
    assert nano_client.api_key == api_key, "Nano Banana client should store API key"
    assert nano_client.max_retries > 0, "Should have retry configuration"
