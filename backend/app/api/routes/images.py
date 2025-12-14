"""Image upload and management routes."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from google.cloud.firestore_v1 import Client

from app.api.dependencies import get_current_active_user
from app.db.base import Collections, get_db
from app.db.firestore_models import ImageModel, create_document, get_document, delete_document
from app.db.models import User
from app.schemas.image import ImageDeleteResponse, ImageInfo, ImageUploadResponse
from app.services.image_validation_service import image_validation_service
from app.services.storage_service import storage_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db)
) -> ImageUploadResponse:
    """
    Upload a patient image.
    
    Validates the image format, size, and quality before uploading to storage.
    Stores metadata in Firestore.
    
    Args:
        file: Image file to upload (JPEG, PNG, or WebP, max 10MB)
        current_user: Authenticated user
        db: Firestore database client
        
    Returns:
        ImageUploadResponse with image ID, URL, and metadata
        
    Raises:
        HTTPException: If validation fails or upload errors occur
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Create BytesIO object for validation
        from io import BytesIO
        file_data = BytesIO(file_content)
        
        # Validate image
        validation_result = image_validation_service.validate_image(
            file_data,
            file.filename or "image.jpg"
        )
        
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Image validation failed: {validation_result.error_message}"
            )
        
        # Reset file pointer for upload
        file_data.seek(0)
        
        # Determine content type
        content_type = file.content_type or "image/jpeg"
        if validation_result.format == "JPEG":
            content_type = "image/jpeg"
        elif validation_result.format == "PNG":
            content_type = "image/png"
        elif validation_result.format == "WEBP":
            content_type = "image/webp"
        
        # Upload to storage
        image_id, public_url = storage_service.upload_image(
            file_data,
            content_type,
            file.filename or "image.jpg"
        )
        
        # Create image metadata in Firestore
        image_model = ImageModel(
            id=image_id,
            user_id=current_user.id,
            url=public_url,
            width=validation_result.width,
            height=validation_result.height,
            format=validation_result.format,
            size_bytes=validation_result.size_bytes,
            original_filename=file.filename or "image.jpg",
            uploaded_at=datetime.utcnow()
        )
        
        await create_document(db, Collections.IMAGES, image_model)
        
        # Return response
        return ImageUploadResponse(
            id=image_id,
            url=public_url,
            width=validation_result.width,
            height=validation_result.height,
            format=validation_result.format,
            size_bytes=validation_result.size_bytes,
            uploaded_at=image_model.uploaded_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.get("/{image_id}", response_model=ImageInfo)
async def get_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db)
) -> ImageInfo:
    """
    Get image metadata by ID.
    
    Args:
        image_id: Unique image identifier
        current_user: Authenticated user
        db: Firestore database client
        
    Returns:
        ImageInfo with image metadata
        
    Raises:
        HTTPException: If image not found or access denied
    """
    try:
        # Get image metadata from Firestore
        image_data = await get_document(db, Collections.IMAGES, image_id)
        
        if not image_data:
            raise HTTPException(
                status_code=404,
                detail=f"Image {image_id} not found"
            )
        
        # Check if user has access to this image
        if image_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this image"
            )
        
        return ImageInfo(**image_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve image: {str(e)}"
        )


@router.delete("/{image_id}", response_model=ImageDeleteResponse)
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Client = Depends(get_db)
) -> ImageDeleteResponse:
    """
    Delete image by ID.
    
    Removes image from storage and deletes metadata from Firestore.
    
    Args:
        image_id: Unique image identifier
        current_user: Authenticated user
        db: Firestore database client
        
    Returns:
        ImageDeleteResponse with deletion status
        
    Raises:
        HTTPException: If image not found or access denied
    """
    try:
        # Get image metadata from Firestore
        image_data = await get_document(db, Collections.IMAGES, image_id)
        
        if not image_data:
            raise HTTPException(
                status_code=404,
                detail=f"Image {image_id} not found"
            )
        
        # Check if user has access to this image
        if image_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to this image"
            )
        
        # Get file extension from format
        format_ext_map = {
            "JPEG": ".jpg",
            "PNG": ".png",
            "WEBP": ".webp"
        }
        file_extension = format_ext_map.get(image_data.get("format", "JPEG"), ".jpg")
        
        # Delete from storage
        storage_deleted = storage_service.delete_image(image_id, file_extension)
        
        # Delete metadata from Firestore
        await delete_document(db, Collections.IMAGES, image_id)
        
        return ImageDeleteResponse(
            success=True,
            message=f"Image {image_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )
