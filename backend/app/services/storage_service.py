"""Object storage service for image uploads using Google Cloud Storage."""
import uuid
from datetime import timedelta
from typing import BinaryIO, Optional

from google.cloud import storage
from google.oauth2 import service_account

from app.config import settings


class StorageService:
    """Service for managing image uploads to Google Cloud Storage."""

    def __init__(self):
        """Initialize Google Cloud Storage client."""
        self.use_gcs = True
        try:
            if settings.gcs_credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.gcs_credentials_path
                )
                self.client = storage.Client(
                    credentials=credentials,
                    project=settings.gcs_project_id
                )
            else:
                # Use default credentials (for production with service account)
                self.client = storage.Client(project=settings.gcs_project_id)
            
            self.bucket_name = settings.gcs_bucket_name
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Test if bucket exists
            if not self.bucket.exists():
                print(f"Warning: GCS bucket '{self.bucket_name}' does not exist. Falling back to local storage.")
                self.use_gcs = False
                self._init_local_storage()
        except Exception as e:
            print(f"Warning: Failed to initialize GCS: {e}. Falling back to local storage.")
            self.use_gcs = False
            self._init_local_storage()
    
    def _init_local_storage(self):
        """Initialize local storage fallback."""
        from app.services.local_storage_service import LocalStorageService
        self.local_storage = LocalStorageService()

    def upload_image(
        self,
        file_data: BinaryIO,
        content_type: str,
        original_filename: str
    ) -> tuple[str, str]:
        """
        Upload an image to Google Cloud Storage with unique filename.
        
        Args:
            file_data: Binary file data to upload
            content_type: MIME type of the file (e.g., 'image/jpeg')
            original_filename: Original filename for reference
            
        Returns:
            Tuple of (image_id, public_url)
        """
        # Use local storage if GCS is not available
        if not self.use_gcs:
            return self.local_storage.upload_image(file_data, content_type, original_filename)
        
        # Generate unique filename
        file_extension = self._get_file_extension(original_filename, content_type)
        image_id = str(uuid.uuid4())
        blob_name = f"images/{image_id}{file_extension}"
        
        # Create blob and upload
        blob = self.bucket.blob(blob_name)
        blob.content_type = content_type
        
        # Upload file data
        file_data.seek(0)  # Reset file pointer to beginning
        blob.upload_from_file(file_data, content_type=content_type)
        
        # Make blob publicly readable
        blob.make_public()
        
        # Return image ID and public URL
        return image_id, blob.public_url

    def get_image_url(self, image_id: str, file_extension: str = ".jpg") -> Optional[str]:
        """
        Get the public URL for an uploaded image.
        
        Args:
            image_id: Unique identifier for the image
            file_extension: File extension (default: .jpg)
            
        Returns:
            Public URL or None if image doesn't exist
        """
        blob_name = f"images/{image_id}{file_extension}"
        blob = self.bucket.blob(blob_name)
        
        if blob.exists():
            return blob.public_url
        return None

    def get_signed_url(
        self,
        image_id: str,
        file_extension: str = ".jpg",
        expiration_minutes: int = 60
    ) -> Optional[str]:
        """
        Generate a signed URL for temporary access to an image.
        
        Args:
            image_id: Unique identifier for the image
            file_extension: File extension (default: .jpg)
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL or None if image doesn't exist
        """
        blob_name = f"images/{image_id}{file_extension}"
        blob = self.bucket.blob(blob_name)
        
        if not blob.exists():
            return None
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        
        return url

    def delete_image(self, image_id: str, file_extension: str = ".jpg") -> bool:
        """
        Delete an image from storage.
        
        Args:
            image_id: Unique identifier for the image
            file_extension: File extension (default: .jpg)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        blob_name = f"images/{image_id}{file_extension}"
        blob = self.bucket.blob(blob_name)
        
        try:
            blob.delete()
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


# Global storage service instance
storage_service = StorageService()
