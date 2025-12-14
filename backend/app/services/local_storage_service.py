"""Local file storage service for development when GCS is not available."""
import os
import uuid
from pathlib import Path
from typing import BinaryIO, Optional


class LocalStorageService:
    """Service for managing image uploads to local filesystem."""

    def __init__(self, storage_dir: str = "./storage/images"):
        """Initialize local storage service."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "http://localhost:8000/storage/images"

    def upload_image(
        self,
        file_data: BinaryIO,
        content_type: str,
        original_filename: str
    ) -> tuple[str, str]:
        """
        Upload an image to local storage with unique filename.
        
        Args:
            file_data: Binary file data to upload
            content_type: MIME type of the file (e.g., 'image/jpeg')
            original_filename: Original filename for reference
            
        Returns:
            Tuple of (image_id, public_url)
        """
        # Generate unique filename
        file_extension = self._get_file_extension(original_filename, content_type)
        image_id = str(uuid.uuid4())
        filename = f"{image_id}{file_extension}"
        filepath = self.storage_dir / filename
        
        # Write file to disk
        file_data.seek(0)
        with open(filepath, 'wb') as f:
            f.write(file_data.read())
        
        # Return image ID and public URL
        public_url = f"{self.base_url}/{filename}"
        return image_id, public_url

    def get_image_url(self, image_id: str, file_extension: str = ".jpg") -> Optional[str]:
        """
        Get the public URL for an uploaded image.
        
        Args:
            image_id: Unique identifier for the image
            file_extension: File extension (default: .jpg)
            
        Returns:
            Public URL or None if image doesn't exist
        """
        filename = f"{image_id}{file_extension}"
        filepath = self.storage_dir / filename
        
        if filepath.exists():
            return f"{self.base_url}/{filename}"
        return None

    def delete_image(self, image_id: str, file_extension: str = ".jpg") -> bool:
        """
        Delete an image from storage.
        
        Args:
            image_id: Unique identifier for the image
            file_extension: File extension (default: .jpg)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        filename = f"{image_id}{file_extension}"
        filepath = self.storage_dir / filename
        
        try:
            if filepath.exists():
                filepath.unlink()
            return True
        except Exception:
            return False

    def _get_file_extension(self, filename: str, content_type: str) -> str:
        """
        Determine file extension from filename or content type.
        
        Args:
            filename: Original filename
            content_type: MIME type
            
        Returns:
            File extension with leading dot
        """
        # Try to get extension from filename
        if "." in filename:
            ext = filename.rsplit(".", 1)[1].lower()
            return f".{ext}"
        
        # Fallback to content type
        content_type_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        
        return content_type_map.get(content_type, ".jpg")
