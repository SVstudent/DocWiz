"""Schemas for image upload and management."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ImageUploadResponse(BaseModel):
    """Response model for image upload."""
    
    id: str = Field(..., description="Unique identifier for the uploaded image")
    url: str = Field(..., description="Public URL to access the image")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Image format (JPEG, PNG, WEBP)")
    size_bytes: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")


class ImageInfo(BaseModel):
    """Information about an uploaded image."""
    
    id: str
    url: str
    width: int
    height: int
    format: str
    size_bytes: int
    uploaded_at: datetime
    user_id: str


class ImageDeleteResponse(BaseModel):
    """Response model for image deletion."""
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
