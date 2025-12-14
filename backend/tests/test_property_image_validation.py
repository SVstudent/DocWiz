"""Property-based tests for image validation consistency.

Feature: docwiz-surgical-platform, Property 1: Image validation consistency
Validates: Requirements 1.1
"""
import io
import pytest
from hypothesis import given, settings, strategies as st
from PIL import Image

from app.services.image_validation_service import ImageValidationService


# Custom strategies for generating test images
@st.composite
def valid_image_strategy(draw):
    """Generate a valid image with allowed format and size."""
    format_choice = draw(st.sampled_from(["JPEG", "PNG", "WEBP"]))
    width = draw(st.integers(min_value=100, max_value=2000))
    height = draw(st.integers(min_value=100, max_value=2000))
    
    # Create a simple image
    if format_choice == "JPEG":
        mode = "RGB"
    elif format_choice == "PNG":
        mode = "RGBA"
    else:  # WEBP
        mode = "RGB"
    
    image = Image.new(mode, (width, height), color=(128, 128, 128))
    
    # Save to bytes
    buffer = io.BytesIO()
    image.save(buffer, format=format_choice, quality=85)
    buffer.seek(0)
    
    return buffer, format_choice, width, height


@st.composite
def invalid_format_image_strategy(draw):
    """Generate an image with invalid format."""
    format_choice = draw(st.sampled_from(["GIF", "BMP", "TIFF"]))
    width = draw(st.integers(min_value=100, max_value=500))
    height = draw(st.integers(min_value=100, max_value=500))
    
    image = Image.new("RGB", (width, height), color=(128, 128, 128))
    
    buffer = io.BytesIO()
    image.save(buffer, format=format_choice)
    buffer.seek(0)
    
    return buffer, format_choice


@st.composite
def oversized_image_strategy(draw):
    """Generate an image that exceeds size limits."""
    # Create a large image that will exceed 10MB when saved
    width = draw(st.integers(min_value=5000, max_value=8000))
    height = draw(st.integers(min_value=5000, max_value=8000))
    
    image = Image.new("RGB", (width, height), color=(255, 0, 0))
    
    buffer = io.BytesIO()
    # Save with high quality to ensure large file size
    image.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer


@pytest.mark.property_test
@given(image_data=valid_image_strategy())
@settings(max_examples=100, deadline=None)
def test_valid_images_are_accepted(image_data):
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any uploaded image file that meets format (JPEG/PNG/WebP), size (≤10MB), 
    and quality requirements, the validation function should accept it.
    """
    buffer, format_choice, width, height = image_data
    validation_service = ImageValidationService()
    
    # Validate the image
    result = validation_service.validate_image(buffer, f"test.{format_choice.lower()}")
    
    # Check file size
    buffer.seek(0, 2)
    file_size = buffer.tell()
    buffer.seek(0)
    
    # If file size is within limits, should be valid
    if file_size <= ImageValidationService.MAX_FILE_SIZE_BYTES:
        assert result.is_valid, f"Valid {format_choice} image should be accepted: {result.error_message}"
        assert result.format == format_choice
        assert result.width == width
        assert result.height == height
    else:
        # If file size exceeds limit, should be rejected
        assert not result.is_valid
        assert "size" in result.error_message.lower()


@pytest.mark.property_test
@given(image_data=invalid_format_image_strategy())
@settings(max_examples=100, deadline=None)
def test_invalid_format_images_are_rejected(image_data):
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any uploaded image file with unsupported format (not JPEG/PNG/WebP), 
    the validation function should reject it.
    """
    buffer, format_choice = image_data
    validation_service = ImageValidationService()
    
    # Validate the image
    result = validation_service.validate_image(buffer, f"test.{format_choice.lower()}")
    
    # Should be rejected due to invalid format
    assert not result.is_valid, f"Invalid format {format_choice} should be rejected"
    assert "format" in result.error_message.lower() or "unsupported" in result.error_message.lower()


@pytest.mark.property_test
@given(
    width=st.integers(min_value=1, max_value=99),
    height=st.integers(min_value=1, max_value=99)
)
@settings(max_examples=100, deadline=None)
def test_undersized_images_are_rejected(width, height):
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any uploaded image file with dimensions below minimum (100x100), 
    the validation function should reject it.
    """
    validation_service = ImageValidationService()
    
    # Create a small image
    image = Image.new("RGB", (width, height), color=(128, 128, 128))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    
    # Validate the image
    result = validation_service.validate_image(buffer, "test.jpg")
    
    # Should be rejected due to small size
    assert not result.is_valid, f"Image {width}x{height} should be rejected (too small)"
    assert "small" in result.error_message.lower() or "minimum" in result.error_message.lower()


@pytest.mark.property_test
@given(data=st.binary(min_size=0, max_size=100))
@settings(max_examples=100, deadline=None)
def test_invalid_image_data_is_rejected(data):
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any uploaded file that is not a valid image, the validation function should reject it.
    """
    validation_service = ImageValidationService()
    
    buffer = io.BytesIO(data)
    
    # Validate the "image"
    result = validation_service.validate_image(buffer, "test.jpg")
    
    # Should be rejected as invalid image data
    assert not result.is_valid, "Invalid image data should be rejected"


@pytest.mark.property_test
def test_empty_file_is_rejected():
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any uploaded empty file, the validation function should reject it.
    """
    validation_service = ImageValidationService()
    
    buffer = io.BytesIO(b"")
    
    # Validate the empty file
    result = validation_service.validate_image(buffer, "test.jpg")
    
    # Should be rejected as empty
    assert not result.is_valid, "Empty file should be rejected"
    assert "empty" in result.error_message.lower()


@pytest.mark.property_test
@given(
    format_choice=st.sampled_from(["JPEG", "PNG", "WEBP"]),
    width=st.integers(min_value=100, max_value=1000),
    height=st.integers(min_value=100, max_value=1000)
)
@settings(max_examples=100, deadline=None)
def test_validation_consistency_across_formats(format_choice, width, height):
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any valid image format (JPEG/PNG/WebP) with valid dimensions and size,
    the validation function should consistently accept it regardless of format.
    """
    validation_service = ImageValidationService()
    
    # Create image in specified format
    if format_choice == "JPEG":
        mode = "RGB"
    elif format_choice == "PNG":
        mode = "RGBA"
    else:  # WEBP
        mode = "RGB"
    
    image = Image.new(mode, (width, height), color=(100, 150, 200))
    buffer = io.BytesIO()
    image.save(buffer, format=format_choice, quality=85)
    buffer.seek(0)
    
    # Check file size
    buffer.seek(0, 2)
    file_size = buffer.tell()
    buffer.seek(0)
    
    # Validate the image
    result = validation_service.validate_image(buffer, f"test.{format_choice.lower()}")
    
    # If within size limits, should be valid
    if file_size <= ImageValidationService.MAX_FILE_SIZE_BYTES:
        assert result.is_valid, f"Valid {format_choice} image should be accepted: {result.error_message}"
        assert result.format == format_choice
        assert result.width == width
        assert result.height == height
        assert result.size_bytes == file_size
    else:
        assert not result.is_valid
        assert "size" in result.error_message.lower()
