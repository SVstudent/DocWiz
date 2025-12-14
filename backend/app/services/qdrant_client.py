"""Qdrant vector database client for similarity search."""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from qdrant_client import QdrantClient as QdrantClientSDK
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import settings

logger = logging.getLogger(__name__)


class QdrantConnectionError(Exception):
    """Raised when connection to Qdrant fails."""
    pass


class QdrantOperationError(Exception):
    """Raised when Qdrant operation fails."""
    pass


class QdrantClient:
    """Client for Qdrant vector database operations."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
    ):
        """
        Initialize Qdrant client.

        Args:
            host: Qdrant host. If not provided, uses settings.qdrant_host
            port: Qdrant port. If not provided, uses settings.qdrant_port
            collection_name: Collection name. If not provided, uses settings.qdrant_collection_name
        """
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.vector_size = 768  # Standard embedding size for image models
        
        try:
            self.client = QdrantClientSDK(host=self.host, port=self.port)
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise QdrantConnectionError(f"Failed to connect to Qdrant: {e}")

    async def ensure_collection_exists(self) -> None:
        """
        Ensure the collection exists, create it if it doesn't.

        The collection stores image embeddings with metadata:
        - procedure_type: Type of surgical procedure
        - age_range: Patient age range (e.g., "20-30", "30-40")
        - outcome_rating: Quality rating of the outcome (0.0-1.0)
        - patient_id: Anonymized patient identifier
        - visualization_id: ID of the visualization result
        - created_at: Timestamp of creation

        Raises:
            QdrantOperationError: If collection creation fails
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                
                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,  # Cosine similarity for image embeddings
                    ),
                )
                
                # Create payload indexes for efficient filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="procedure_type",
                    field_schema="keyword",
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="age_range",
                    field_schema="keyword",
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="outcome_rating",
                    field_schema="float",
                )
                
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

        except UnexpectedResponse as e:
            logger.error(f"Qdrant API error: {e}")
            raise QdrantOperationError(f"Failed to ensure collection exists: {e}")
        except Exception as e:
            logger.error(f"Unexpected error ensuring collection: {e}")
            raise QdrantOperationError(f"Unexpected error: {e}")

    async def upsert_embedding(
        self,
        point_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> None:
        """
        Store or update an embedding with metadata.

        Args:
            point_id: Unique identifier for the point
            embedding: Vector embedding (must be size self.vector_size)
            metadata: Metadata dictionary containing:
                - procedure_type: str
                - age_range: str (e.g., "20-30")
                - outcome_rating: float (0.0-1.0)
                - patient_id: str (anonymized)
                - visualization_id: str
                - created_at: str (ISO format timestamp)

        Raises:
            QdrantOperationError: If upsert operation fails
            ValueError: If embedding size is incorrect
        """
        if len(embedding) != self.vector_size:
            raise ValueError(
                f"Embedding size {len(embedding)} does not match expected size {self.vector_size}"
            )

        try:
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=metadata,
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.info(f"Upserted embedding for point {point_id}")

        except UnexpectedResponse as e:
            logger.error(f"Qdrant API error during upsert: {e}")
            raise QdrantOperationError(f"Failed to upsert embedding: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during upsert: {e}")
            raise QdrantOperationError(f"Unexpected error: {e}")

    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        procedure_type: Optional[str] = None,
        age_range: Optional[str] = None,
        min_outcome_rating: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings with optional filtering.

        Args:
            query_embedding: Query vector embedding
            limit: Maximum number of results to return
            procedure_type: Filter by procedure type (optional)
            age_range: Filter by age range (optional)
            min_outcome_rating: Minimum outcome rating filter (optional)

        Returns:
            List of search results, each containing:
                - id: Point ID
                - score: Similarity score
                - payload: Metadata dictionary

        Raises:
            QdrantOperationError: If search operation fails
            ValueError: If query embedding size is incorrect
        """
        if len(query_embedding) != self.vector_size:
            raise ValueError(
                f"Query embedding size {len(query_embedding)} does not match expected size {self.vector_size}"
            )

        try:
            # Build filter conditions
            filter_conditions = []

            if procedure_type:
                filter_conditions.append(
                    FieldCondition(
                        key="procedure_type",
                        match=MatchValue(value=procedure_type),
                    )
                )

            if age_range:
                filter_conditions.append(
                    FieldCondition(
                        key="age_range",
                        match=MatchValue(value=age_range),
                    )
                )

            if min_outcome_rating is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="outcome_rating",
                        range=Range(gte=min_outcome_rating),
                    )
                )

            # Create filter object if we have conditions
            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)

            # Perform search using query_points (the new API method)
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                query_filter=search_filter,
            )

            # Format results - query_points returns a QueryResponse with .points
            results = []
            for result in search_results.points:
                results.append({
                    "id": str(result.id),
                    "score": result.score,
                    "payload": result.payload,
                })

            logger.info(
                f"Found {len(results)} similar embeddings "
                f"(procedure_type={procedure_type}, age_range={age_range}, "
                f"min_outcome_rating={min_outcome_rating})"
            )

            return results

        except UnexpectedResponse as e:
            logger.error(f"Qdrant API error during search: {e}")
            raise QdrantOperationError(f"Failed to search embeddings: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise QdrantOperationError(f"Unexpected error: {e}")

    async def delete_embedding(self, point_id: str) -> None:
        """
        Delete an embedding by ID.

        Args:
            point_id: ID of the point to delete

        Raises:
            QdrantOperationError: If delete operation fails
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id],
            )
            logger.info(f"Deleted embedding for point {point_id}")

        except UnexpectedResponse as e:
            logger.error(f"Qdrant API error during delete: {e}")
            raise QdrantOperationError(f"Failed to delete embedding: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during delete: {e}")
            raise QdrantOperationError(f"Unexpected error: {e}")

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary containing collection information

        Raises:
            QdrantOperationError: If operation fails
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else self.vector_size,
                "points_count": collection_info.points_count if hasattr(collection_info, 'points_count') else 0,
                "status": collection_info.status if hasattr(collection_info, 'status') else "unknown",
            }

        except UnexpectedResponse as e:
            logger.error(f"Qdrant API error getting collection info: {e}")
            raise QdrantOperationError(f"Failed to get collection info: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting collection info: {e}")
            raise QdrantOperationError(f"Unexpected error: {e}")
