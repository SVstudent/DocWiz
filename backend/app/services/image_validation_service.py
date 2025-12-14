"""Image validation service for uploaded images."""
from io import BytesIO
from typing import BinaryIO, Optional

from PIL import Image


class ImageValidationError(Exception):
    """Exception raised when image validation fails."""
    pass


class ImageValidationResult:
    """Result of image validation."""
    
    def __init__(
        self,
        is_valid: bool,
        error_message: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: Optional[str] = None,
        size_bytes: Optional[int] = None
    ):
        self.is_valid = is_valid
        self.error_message = error_message
        self.width = width
        self.height = height
        self.format = format
        self.size_bytes = size_bytes


class ImageValidationService:
    """Service for validating uploaded images."""
    
    # Validation constraints
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MIN_WIDTH = 100
    MIN_HEIGHT = 100
    MAX_WIDTH = 8000
    MAX_HEIGHT = 8000
    
    def validate_image(
        self,
        file_data: BinaryIO,
        filename: str
    ) -> ImageValidationResult:
        """
        Validate an uploaded image file.
        
        Checks:
        - Format (JPEG, PNG, WebP)
        - File size (max 10MB)
        - Image dimensions and quality
        - Malicious content detection
        
        Args:
            file_data: Binary file data
            filename: Original filename
            
        Returns:
            ImageValidationResult with validation status and details
        """
        try:
            # Read file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            # Validate file size
            if file_size > self.MAX_FILE_SIZE_BYTES:
                return ImageValidationResult(
                    is_valid=False,
                    error_message=f"File size exceeds maximum of {self.MAX_FILE_SIZE_MB}MB"
                )
            
            if file_size == 0:
                return ImageValidationResult(
                    is_valid=False,
                    error_message="File is empty"
                )
            
            # Try to open image with PIL
            try:
                image = Image.open(file_data)
                image.verify()  # Verify it's a valid image
                
                # Re-open after verify (verify closes the file)
                file_data.seek(0)
                image = Image.open(file_data)
                
            except Exception as e:
                return ImageValidationResult(
                    is_valid=False,
                    error_message=f"Invalid image file: {str(e)}"
                )
            
            # Validate format
            if image.format not in self.ALLOWED_FORMATS:
                return ImageValidationResult(
                    is_valid=False,
                    error_message=f"Unsupported format: {image.format}. Allowed formats: {', '.join(self.ALLOWED_FORMATS)}"
                )
            
            # Validate dimensions
            width, height = image.size
            
            if width < self.MIN_WIDTH or height < self.MIN_HEIGHT:
                return ImageValidationResult(
                    is_valid=False,
                    error_message=f"Image too small. Minimum dimensions: {self.MIN_WIDTH}x{self.MIN_HEIGHT}px"
                )
            
            if width > self.MAX_WIDTH or height > self.MAX_HEIGHT:
                return ImageValidationResult(
                    is_valid=False,
                    error_message=f"Image too large. Maximum dimensions: {self.MAX_WIDTH}x{self.MAX_HEIGHT}px"
                )
            
            # Check for malicious content (basic checks)
            if not self._check_image_safety(image):
                return ImageValidationResult(
                    is_valid=False,
                    error_message="Image failed safety checks"
                )
            
            # Reset file pointer for subsequent operations
            file_data.seek(0)
            
            # Return successful validation
            return ImageValidationResult(
                is_valid=True,
                width=width,
                height=height,
                format=image.format,
                size_bytes=file_size
            )
            
        except Exception as e:
            return ImageValidationResult(
                is_valid=False,
                error_message=f"Validation error: {str(e)}"
            )
    
    def _check_image_safety(self, image: Image.Image) -> bool:
        """
        Perform basic safety checks on the image.
        
        Args:
            image: PIL Image object
            
        Returns:
            True if image passes safety checks, False otherwise
        """
        try:
            # Check if image has valid mode (expanded to include more common modes)
            valid_modes = {"RGB", "RGBA", "L", "P", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"}
            if image.mode not in valid_modes:
                return False
            
            # Check for excessive metadata (potential exploit)
            if hasattr(image, 'info') and len(str(image.info)) > 50000:
                return False
            
            # Basic dimension sanity check
            width, height = image.size
            if width <= 0 or height <= 0:
                return False
            
            # Try to access pixel data (will fail if corrupted)
            # Use getpixel instead of load() for less strict checking
            try:
                image.getpixel((0, 0))
            except Exception:
                # If getpixel fails, try converting to RGB first
                try:
                    rgb_image = image.convert('RGB')
                    rgb_image.getpixel((0, 0))
                except Exception:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_image_info(self, file_data: BinaryIO) -> dict:
        """
        Extract information from an image file.
        
        Args:
            file_data: Binary file data
            
        Returns:
            Dictionary with image information
        """
        try:
            file_data.seek(0)
            image = Image.open(file_data)
            
            width, height = image.size
            
            return {
                "width": width,
                "height": height,
                "format": image.format,
                "mode": image.mode,
                "has_transparency": image.mode in ("RGBA", "LA", "P")
            }
        except Exception as e:
            return {"error": str(e)}


# Global image validation service instance
image_validation_service = ImageValidationService()
