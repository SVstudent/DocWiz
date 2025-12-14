"""Property-based tests for Freepik integration.

Feature: docwiz-surgical-platform, Property 28: Freepik integration
Validates: Requirements 9.3
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from hypothesis import given, settings, strategies as st, HealthCheck
from decimal import Decimal

from app.services.freepik_client import FreepikClient, FreepikAPIError


# Strategy for generating cost data
@st.composite
def cost_data_strategy(draw):
    """Generate cost breakdown data for infographic generation."""
    total_cost = draw(st.integers(min_value=5000, max_value=50000))
    surgeon_fee = draw(st.integers(min_value=1000, max_value=total_cost // 2))
    facility_fee = draw(st.integers(min_value=500, max_value=total_cost // 3))
    anesthesia_fee = draw(st.integers(min_value=500, max_value=5000))
    post_op_care = total_cost - surgeon_fee - facility_fee - anesthesia_fee
    
    # Ensure post_op_care is positive
    if post_op_care < 0:
        post_op_care = draw(st.integers(min_value=500, max_value=2000))
        total_cost = surgeon_fee + facility_fee + anesthesia_fee + post_op_care
    
    insurance_coverage = draw(st.integers(min_value=0, max_value=int(total_cost * 0.8)))
    patient_responsibility = total_cost - insurance_coverage
    
    return {
        "total_cost": total_cost,
        "surgeon_fee": surgeon_fee,
        "facility_fee": facility_fee,
        "anesthesia_fee": anesthesia_fee,
        "post_op_care": post_op_care,
        "insurance_coverage": insurance_coverage,
        "patient_responsibility": patient_responsibility
    }


# Strategy for generating image prompts
@st.composite
def image_prompt_strategy(draw):
    """Generate image generation prompts."""
    subjects = ["medical cost breakdown", "surgical procedure infographic", "healthcare pricing chart"]
    styles = ["professional", "modern", "minimal", "clean"]
    
    subject = draw(st.sampled_from(subjects))
    style = draw(st.sampled_from(styles))
    
    return f"Create a {style} {subject} with clear data visualization"


@pytest.mark.property_test
@given(
    cost_data=cost_data_strategy(),
    format=st.sampled_from(["png", "jpeg"]),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_freepik_api_called_for_infographic(cost_data, format):
    """
    Feature: docwiz-surgical-platform, Property 28: Freepik integration
    
    For any enhanced visualization request, the system should call Freepik API 
    for image generation or enhancement.
    
    This test verifies that Freepik API is called when generating cost infographics.
    """
    # Mock the HTTP client to avoid actual API calls
    mock_response = {
        "data": [
            {
                "url": "https://example.com/generated-infographic.png",
                "id": "test-image-id-123"
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
        client = FreepikClient(api_key="test-key")
        result = await client.generate_cost_infographic(cost_data, format=format)
        
        # Verify Freepik API was called
        assert mock_client.post.called, "Freepik API should be called for infographic generation"
        
        # Verify the call was made to the correct endpoint
        call_args = mock_client.post.call_args
        assert "text-to-image" in call_args[0][0], "Should call text-to-image endpoint"
        
        # Verify result contains expected fields
        assert "image_url" in result, "Result should contain image_url"
        assert "format" in result, "Result should contain format"
        assert result["format"] == format, f"Result format should match requested format: {format}"


@pytest.mark.property_test
@given(
    prompt=image_prompt_strategy(),
    width=st.integers(min_value=512, max_value=2048),
    height=st.integers(min_value=512, max_value=2048),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_freepik_image_generation(prompt, width, height):
    """
    Feature: docwiz-surgical-platform, Property 28: Freepik integration
    
    For any image generation request with valid parameters, the system should
    call Freepik API and return image data.
    
    This test verifies general image generation functionality.
    """
    # Mock the HTTP client
    mock_response = {
        "data": [
            {
                "url": f"https://example.com/generated-{width}x{height}.png",
                "id": "test-image-id"
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
        client = FreepikClient(api_key="test-key")
        result = await client.generate_image(
            prompt=prompt,
            width=width,
            height=height
        )
        
        # Verify API was called
        assert mock_client.post.called, "Freepik API should be called"
        
        # Verify request payload contains correct dimensions
        call_kwargs = mock_client.post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["width"] == width, "Request should include correct width"
        assert payload["height"] == height, "Request should include correct height"
        
        # Verify result
        assert "image_url" in result, "Result should contain image_url"
        assert result["width"] == width, "Result should contain correct width"
        assert result["height"] == height, "Result should contain correct height"


@pytest.mark.property_test
@given(
    cost_data=cost_data_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_freepik_retry_logic_on_failure(cost_data):
    """
    Feature: docwiz-surgical-platform, Property 28: Freepik integration
    
    For any API request that fails, the system should implement retry logic
    with exponential backoff.
    
    This test verifies that retry logic is properly implemented for Freepik.
    """
    with patch('httpx.AsyncClient') as mock_client_class:
        # Setup mock to fail
        mock_client = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 500
        mock_response_obj.text = "Internal Server Error"
        mock_client.post.return_value = mock_response_obj
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Create client
        client = FreepikClient(api_key="test-key")
        max_retries = client.max_retries
        
        # Attempt to generate infographic (should fail and retry)
        with pytest.raises(FreepikAPIError):
            await client.generate_cost_infographic(cost_data)
        
        # Verify retry attempts were made
        assert mock_client.post.call_count == max_retries, (
            f"Should retry {max_retries} times on failure"
        )


@pytest.mark.property_test
@given(
    cost_data=cost_data_strategy(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@pytest.mark.asyncio
async def test_freepik_authentication_handling(cost_data):
    """
    Feature: docwiz-surgical-platform, Property 28: Freepik integration
    
    For any API request with invalid authentication, the system should
    handle authentication errors appropriately.
    
    This test verifies proper authentication error handling.
    """
    with patch('httpx.AsyncClient') as mock_client_class:
        # Setup mock to return authentication error
        mock_client = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 401
        mock_response_obj.text = "Unauthorized"
        mock_client.post.return_value = mock_response_obj
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Create client
        client = FreepikClient(api_key="invalid-key")
        
        # Attempt to generate infographic (should raise authentication error)
        with pytest.raises(FreepikAPIError) as exc_info:
            await client.generate_cost_infographic(cost_data)
        
        # Verify error message mentions authentication
        assert "Authentication failed" in str(exc_info.value) or "invalid API key" in str(exc_info.value)


@pytest.mark.property_test
@given(
    api_key=st.text(min_size=10, max_size=50),
)
@settings(
    max_examples=100,
    deadline=None,
)
def test_freepik_client_initialization(api_key):
    """
    Feature: docwiz-surgical-platform, Property 28: Freepik integration
    
    For any valid API key, the Freepik client should initialize properly
    and store the API key for subsequent requests.
    
    This test verifies proper client initialization.
    """
    # Test Freepik client initialization
    client = FreepikClient(api_key=api_key)
    assert client.api_key == api_key, "Freepik client should store API key"
    assert client.max_retries > 0, "Should have retry configuration"
    assert client.base_url, "Should have base URL configured"


@pytest.mark.property_test
@given(
    cost_data=cost_data_strategy(),
    style=st.sampled_from(["professional", "modern", "minimal"]),
)
@settings(
    max_examples=100,
    deadline=None,
)
def test_infographic_prompt_generation(cost_data, style):
    """
    Feature: docwiz-surgical-platform, Property 28: Freepik integration
    
    For any cost data and style, the system should generate a comprehensive
    prompt for infographic creation.
    
    This test verifies prompt generation logic.
    """
    client = FreepikClient(api_key="test-key")
    prompt = client._build_infographic_prompt(cost_data, style)
    
    # Verify prompt contains essential information (checking for formatted values)
    assert "Total Procedure Cost" in prompt, "Prompt should include total cost label"
    assert "Surgeon Fee" in prompt, "Prompt should include surgeon fee label"
    assert "Facility Fee" in prompt, "Prompt should include facility fee label"
    assert "Anesthesia" in prompt, "Prompt should include anesthesia label"
    assert "Insurance Coverage" in prompt, "Prompt should include insurance coverage label"
    assert style in prompt, "Prompt should include requested style"
    
    # Verify prompt includes design requirements
    assert "chart" in prompt.lower(), "Prompt should mention chart visualization"
    assert "professional" in prompt.lower() or "medical" in prompt.lower(), "Prompt should mention medical context"
