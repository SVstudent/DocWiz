"""Gemini API client for surgical visualization generation."""
import asyncio
import logging
from typing import Optional, Dict, Any
from io import BytesIO

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Base exception for Gemini API errors."""
    pass


class GeminiRateLimitError(GeminiAPIError):
    """Raised when rate limit is exceeded."""
    pass


class GeminiClient:
    """Client for Google Gemini 2.5 Flash Image API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key. If not provided, uses settings.gemini_api_key
        """
        self.api_key = api_key or settings.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash-exp"
        self.max_retries = 3
        self.initial_retry_delay = 1.0  # seconds

    async def generate_image(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Generate surgical preview image using Gemini.

        Args:
            image_data: Source image bytes
            prompt: Surgical modification prompt
            mime_type: Image MIME type (image/jpeg, image/png, image/webp)

        Returns:
            Dict containing generated image data and metadata

        Raises:
            GeminiAPIError: If API call fails after retries
            GeminiRateLimitError: If rate limit is exceeded
        """
        logger.info(f"Generating image with prompt: {prompt[:100]}...")

        for attempt in range(self.max_retries):
            try:
                result = await self._make_request(image_data, prompt, mime_type)
                logger.info("Image generation successful")
                return result
            except GeminiRateLimitError:
                # Don't retry rate limit errors
                logger.error("Rate limit exceeded")
                raise
            except GeminiAPIError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Image generation failed after {self.max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff
                delay = self.initial_retry_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)

        raise GeminiAPIError("Max retries exceeded")

    async def _make_request(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Make API request to Gemini.

        Args:
            image_data: Source image bytes
            prompt: Surgical modification prompt
            mime_type: Image MIME type

        Returns:
            Dict containing API response

        Raises:
            GeminiAPIError: If API request fails
            GeminiRateLimitError: If rate limit is exceeded
        """
        import base64

        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Construct request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,  # Lower temperature for more consistent medical results
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 4096,
            }
        }

        url = f"{self.base_url}/models/{self.model}:generateContent"
        params = {"key": self.api_key}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    params=params
                )

                # Log request/response for debugging
                logger.debug(f"Request URL: {url}")
                logger.debug(f"Response status: {response.status_code}")

                if response.status_code == 429:
                    raise GeminiRateLimitError("Rate limit exceeded")

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"API error response: {error_detail}")
                    raise GeminiAPIError(
                        f"API request failed with status {response.status_code}: {error_detail}"
                    )

                result = response.json()
                logger.debug(f"Response data: {result}")

                # Extract generated content
                if "candidates" not in result or not result["candidates"]:
                    raise GeminiAPIError("No candidates in response")

                candidate = result["candidates"][0]
                if "content" not in candidate:
                    raise GeminiAPIError("No content in candidate")

                return {
                    "content": candidate["content"],
                    "finish_reason": candidate.get("finishReason"),
                    "safety_ratings": candidate.get("safetyRatings", []),
                    "raw_response": result
                }

            except httpx.TimeoutException as e:
                logger.error(f"Request timeout: {e}")
                raise GeminiAPIError(f"Request timeout: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise GeminiAPIError(f"Request error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise GeminiAPIError(f"Unexpected error: {e}")

    async def validate_image(self, image_data: bytes) -> bool:
        """
        Validate image for processing.

        Args:
            image_data: Image bytes to validate

        Returns:
            True if image is valid, False otherwise
        """
        try:
            # Check file size (max 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                logger.warning("Image exceeds 10MB size limit")
                return False

            # Validate image format using PIL
            image = Image.open(BytesIO(image_data))
            
            # Check format
            if image.format not in ['JPEG', 'PNG', 'WEBP']:
                logger.warning(f"Unsupported image format: {image.format}")
                return False

            # Check dimensions (reasonable limits)
            width, height = image.size
            if width < 100 or height < 100:
                logger.warning(f"Image too small: {width}x{height}")
                return False
            if width > 4096 or height > 4096:
                logger.warning(f"Image too large: {width}x{height}")
                return False

            return True

        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False
