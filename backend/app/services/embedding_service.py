"""Service for generating and managing image embeddings."""
import logging
from typing import List, Dict, Any, Optional
from io import BytesIO
from datetime import datetime
import hashlib

from PIL import Image
import numpy as np

from app.services.qdrant_client import QdrantClient, QdrantOperationError

logger = logging.getLogger(__name__)


class EmbeddingGenerationError(Exception):
    """Raised when embedding generation fails."""
    pass


class EmbeddingService:
    """Service for generating and storing image embeddings."""

    def __init__(self, qdrant_client: Optional[QdrantClient] = None):
        """
        Initialize embedding service.

        Args:
            qdrant_client: Qdrant client instance. If not provided, creates a new one.
        """
        self.qdrant_client = qdrant_client or QdrantClient()
        self.embedding_size = 768  # Standard size for image embeddings

    async def generate_embedding(self, image_data: bytes) -> List[float]:
        """
        Generate vector embedding from image data.

        This is a simplified implementation that extracts basic image features.
        In production, this would use a pre-trained model like CLIP or ResNet.

        Args:
            image_data: Image bytes

        Returns:
            List of floats representing the embedding vector

        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        try:
            # Open image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize to standard size for consistency
            target_size = (224, 224)
            image = image.resize(target_size, Image.Resampling.LANCZOS)

            # Convert to numpy array
            img_array = np.array(image, dtype=np.float32)

            # Normalize pixel values to [0, 1]
            img_array = img_array / 255.0

            # Extract features using a simple approach
            # In production, use a pre-trained model like CLIP
            embedding = self._extract_simple_features(img_array)

            # Ensure embedding is the correct size
            if len(embedding) != self.embedding_size:
                # Pad or truncate to match expected size
                if len(embedding) < self.embedding_size:
                    embedding = np.pad(
                        embedding,
                        (0, self.embedding_size - len(embedding)),
                        mode='constant'
                    )
                else:
                    embedding = embedding[:self.embedding_size]

            # Normalize the embedding vector
            embedding = self._normalize_vector(embedding)

            logger.info(f"Generated embedding of size {len(embedding)}")
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embedding: {e}")

    def _extract_simple_features(self, img_array: np.ndarray) -> np.ndarray:
        """
        Extract simple features from image array.

        This is a placeholder implementation. In production, use a pre-trained
        model like CLIP, ResNet, or EfficientNet.

        Args:
            img_array: Normalized image array (H, W, 3)

        Returns:
            Feature vector
        """
        features = []

        # Color histogram features (per channel)
        for channel in range(3):
            hist, _ = np.histogram(img_array[:, :, channel], bins=32, range=(0, 1))
            features.extend(hist / hist.sum())  # Normalize

        # Mean and std per channel
        for channel in range(3):
            features.append(img_array[:, :, channel].mean())
            features.append(img_array[:, :, channel].std())

        # Spatial features (divide image into grid)
        grid_size = 4
        h, w = img_array.shape[:2]
        cell_h, cell_w = h // grid_size, w // grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                cell = img_array[
                    i * cell_h:(i + 1) * cell_h,
                    j * cell_w:(j + 1) * cell_w
                ]
                # Mean color in each cell
                features.extend(cell.mean(axis=(0, 1)))

        # Edge detection features (simple gradient)
        gray = img_array.mean(axis=2)
        grad_x = np.abs(np.diff(gray, axis=1)).mean()
        grad_y = np.abs(np.diff(gray, axis=0)).mean()
        features.extend([grad_x, grad_y])

        # Texture features (local variance)
        for i in range(grid_size):
            for j in range(grid_size):
                cell = img_array[
                    i * cell_h:(i + 1) * cell_h,
                    j * cell_w:(j + 1) * cell_w
                ]
                features.append(cell.std())

        return np.array(features, dtype=np.float32)

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        Normalize vector to unit length.

        Args:
            vector: Input vector

        Returns:
            Normalized vector
        """
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector

    async def store_embedding(
        self,
        image_data: bytes,
        visualization_id: str,
        procedure_type: str,
        age_range: str,
        outcome_rating: float,
        patient_id: str,
    ) -> str:
        """
        Generate and store embedding with metadata.

        Args:
            image_data: Image bytes
            visualization_id: ID of the visualization result
            procedure_type: Type of surgical procedure
            age_range: Patient age range (e.g., "20-30")
            outcome_rating: Quality rating (0.0-1.0)
            patient_id: Anonymized patient ID

        Returns:
            Point ID of the stored embedding

        Raises:
            EmbeddingGenerationError: If generation fails
            QdrantOperationError: If storage fails
        """
        # Generate embedding
        embedding = await self.generate_embedding(image_data)

        # Create unique point ID based on visualization ID
        point_id = self._generate_point_id(visualization_id)

        # Prepare metadata
        metadata = {
            "visualization_id": visualization_id,
            "procedure_type": procedure_type,
            "age_range": age_range,
            "outcome_rating": outcome_rating,
            "patient_id": patient_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Store in Qdrant
        await self.qdrant_client.upsert_embedding(
            point_id=point_id,
            embedding=embedding,
            metadata=metadata,
        )

        logger.info(f"Stored embedding for visualization {visualization_id}")
        return point_id

    async def find_similar_cases(
        self,
        image_data: bytes,
        procedure_type: Optional[str] = None,
        age_range: Optional[str] = None,
        min_outcome_rating: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find similar cases based on image similarity.

        Args:
            image_data: Query image bytes
            procedure_type: Filter by procedure type (optional)
            age_range: Filter by age range (optional)
            min_outcome_rating: Minimum outcome rating (optional)
            limit: Maximum number of results

        Returns:
            List of similar cases with metadata and similarity scores

        Raises:
            EmbeddingGenerationError: If embedding generation fails
            QdrantOperationError: If search fails
        """
        # Generate query embedding
        query_embedding = await self.generate_embedding(image_data)

        # Search for similar embeddings
        results = await self.qdrant_client.search_similar(
            query_embedding=query_embedding,
            limit=limit,
            procedure_type=procedure_type,
            age_range=age_range,
            min_outcome_rating=min_outcome_rating,
        )

        logger.info(f"Found {len(results)} similar cases")
        return results

    def _generate_point_id(self, visualization_id: str) -> str:
        """
        Generate a unique point ID from visualization ID.

        Args:
            visualization_id: Visualization ID

        Returns:
            Unique point ID
        """
        # Use hash to create a consistent ID
        return hashlib.sha256(visualization_id.encode()).hexdigest()[:32]

    async def initialize(self) -> None:
        """
        Initialize the embedding service.

        Ensures the Qdrant collection exists.
        """
        await self.qdrant_client.ensure_collection_exists()
        logger.info("Embedding service initialized")
