"""Freepik API client for cost infographic generation."""
import asyncio
import logging
from typing import Optional, Dict, Any, Literal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class FreepikAPIError(Exception):
    """Base exception for Freepik API errors."""
    pass


class FreepikRateLimitError(FreepikAPIError):
    """Raised when rate limit is exceeded."""
    pass


class FreepikClient:
    """Client for Freepik Studio API for image/video generation."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Freepik client.

        Args:
            api_key: Freepik API key. If not provided, uses settings.freepik_api_key
        """
        self.api_key = api_key or settings.freepik_api_key
        self.base_url = "https://api.freepik.com/v1"
        self.max_retries = 3
        self.initial_retry_delay = 1.0  # seconds

    async def generate_cost_infographic(
        self,
        cost_data: Dict[str, Any],
        format: Literal["png", "jpeg"] = "png",
        style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate visual cost breakdown infographic.

        Args:
            cost_data: Dictionary containing cost breakdown information
            format: Output format (png or jpeg)
            style: Visual style (professional, modern, minimal)

        Returns:
            Dict containing generated infographic URL and metadata

        Raises:
            FreepikAPIError: If API call fails after retries
            FreepikRateLimitError: If rate limit is exceeded
        """
        logger.info(f"Generating cost infographic in {format} format")

        # Build prompt for infographic generation
        prompt = self._build_infographic_prompt(cost_data, style)

        result = await self.generate_image(
            prompt=prompt,
            format=format,
            width=1200,
            height=800
        )

        return result

    async def generate_image(
        self,
        prompt: str,
        format: Literal["png", "jpeg"] = "png",
        width: int = 1024,
        height: int = 1024,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Freepik API.

        Args:
            prompt: Image generation prompt
            format: Output format (png or jpeg)
            width: Image width in pixels
            height: Image height in pixels
            style: Optional style preset

        Returns:
            Dict containing generated image URL and metadata

        Raises:
            FreepikAPIError: If API call fails after retries
            FreepikRateLimitError: If rate limit is exceeded
        """
        logger.info(f"Generating image: {width}x{height} {format}")

        for attempt in range(self.max_retries):
            try:
                result = await self._make_request(
                    prompt=prompt,
                    format=format,
                    width=width,
                    height=height,
                    style=style
                )
                logger.info("Image generation successful")
                return result
            except FreepikRateLimitError:
                # Don't retry rate limit errors
                logger.error("Rate limit exceeded")
                raise
            except FreepikAPIError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Image generation failed after {self.max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff
                delay = self.initial_retry_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)

        raise FreepikAPIError("Max retries exceeded")

    async def _make_request(
        self,
        prompt: str,
        format: str,
        width: int,
        height: int,
        style: Optional[str]
    ) -> Dict[str, Any]:
        """
        Make API request to Freepik.

        Args:
            prompt: Image generation prompt
            format: Output format
            width: Image width
            height: Image height
            style: Optional style preset

        Returns:
            Dict containing API response

        Raises:
            FreepikAPIError: If API request fails
            FreepikRateLimitError: If rate limit is exceeded
        """
        # Construct request payload
        payload = {
            "prompt": prompt,
            "output_format": format,
            "width": width,
            "height": height,
            "num_images": 1
        }

        if style:
            payload["style"] = style

        url = f"{self.base_url}/ai/text-to-image"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )

                # Log request/response for debugging
                logger.debug(f"Request URL: {url}")
                logger.debug(f"Response status: {response.status_code}")

                if response.status_code == 429:
                    raise FreepikRateLimitError("Rate limit exceeded")

                if response.status_code == 401:
                    raise FreepikAPIError("Authentication failed - invalid API key")

                if response.status_code != 200 and response.status_code != 201:
                    error_detail = response.text
                    logger.error(f"API error response: {error_detail}")
                    raise FreepikAPIError(
                        f"API request failed with status {response.status_code}: {error_detail}"
                    )

                result = response.json()
                logger.debug(f"Response data keys: {result.keys()}")

                # Extract image URL from response
                # Note: Actual response structure may vary based on Freepik API version
                if "data" in result and isinstance(result["data"], list) and result["data"]:
                    image_data = result["data"][0]
                    return {
                        "image_url": image_data.get("url"),
                        "image_id": image_data.get("id"),
                        "format": format,
                        "width": width,
                        "height": height,
                        "raw_response": result
                    }
                elif "url" in result:
                    # Alternative response structure
                    return {
                        "image_url": result["url"],
                        "image_id": result.get("id"),
                        "format": format,
                        "width": width,
                        "height": height,
                        "raw_response": result
                    }
                else:
                    raise FreepikAPIError("Unexpected response structure - no image URL found")

            except httpx.TimeoutException as e:
                logger.error(f"Request timeout: {e}")
                raise FreepikAPIError(f"Request timeout: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise FreepikAPIError(f"Request error: {e}")
            except Exception as e:
                if isinstance(e, (FreepikAPIError, FreepikRateLimitError)):
                    raise
                logger.error(f"Unexpected error: {e}")
                raise FreepikAPIError(f"Unexpected error: {e}")

    def _build_infographic_prompt(
        self,
        cost_data: Dict[str, Any],
        style: str
    ) -> str:
        """
        Build prompt for cost infographic generation.

        Args:
            cost_data: Dictionary containing cost breakdown
            style: Visual style preference

        Returns:
            Formatted prompt string
        """
        # Extract cost components
        total_cost = cost_data.get("total_cost", 0)
        surgeon_fee = cost_data.get("surgeon_fee", 0)
        facility_fee = cost_data.get("facility_fee", 0)
        anesthesia_fee = cost_data.get("anesthesia_fee", 0)
        post_op_care = cost_data.get("post_op_care", 0)
        insurance_coverage = cost_data.get("insurance_coverage", 0)
        patient_responsibility = cost_data.get("patient_responsibility", 0)

        prompt = f"""Create a {style} medical cost breakdown infographic with the following information:

Total Procedure Cost: ${total_cost:,.2f}

Cost Components:
- Surgeon Fee: ${surgeon_fee:,.2f}
- Facility Fee: ${facility_fee:,.2f}
- Anesthesia: ${anesthesia_fee:,.2f}
- Post-Op Care: ${post_op_care:,.2f}

Insurance Coverage: ${insurance_coverage:,.2f}
Patient Responsibility: ${patient_responsibility:,.2f}

Design requirements:
- Clean, professional medical aesthetic
- Use surgical blue (#0066CC) as primary color
- Include pie chart or bar chart showing cost breakdown
- Clear typography with good contrast
- Include all numerical values
- Professional layout suitable for patient consultation
- White or light gray background
- No stock photos or decorative elements
- Focus on data visualization and clarity"""

        return prompt

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        fps: int = 30
    ) -> Dict[str, Any]:
        """
        Generate video using Freepik API (for future enhancement).

        Args:
            prompt: Video generation prompt
            duration: Video duration in seconds
            fps: Frames per second

        Returns:
            Dict containing generated video URL and metadata

        Raises:
            FreepikAPIError: If API call fails after retries
        """
        logger.info(f"Generating video: {duration}s at {fps}fps")

        payload = {
            "prompt": prompt,
            "duration": duration,
            "fps": fps
        }

        url = f"{self.base_url}/ai/text-to-video"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )

                if response.status_code == 429:
                    raise FreepikRateLimitError("Rate limit exceeded")

                if response.status_code != 200 and response.status_code != 201:
                    error_detail = response.text
                    raise FreepikAPIError(
                        f"API request failed with status {response.status_code}: {error_detail}"
                    )

                result = response.json()
                return {
                    "video_url": result.get("url"),
                    "video_id": result.get("id"),
                    "duration": duration,
                    "fps": fps,
                    "raw_response": result
                }

            except httpx.TimeoutException as e:
                raise FreepikAPIError(f"Request timeout: {e}")
            except httpx.RequestError as e:
                raise FreepikAPIError(f"Request error: {e}")
