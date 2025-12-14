"""Service for surgical visualization generation and management."""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from io import BytesIO

from app.services.storage_service import StorageService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_client import QdrantClient
from app.db.base import get_db, Collections
from app.db.seed_procedures import get_procedure_by_id

logger = logging.getLogger(__name__)


class VisualizationError(Exception):
    """Base exception for visualization errors."""
    pass


class VisualizationService:
    """Service for generating and managing surgical visualizations using gemini-2.5-flash-image."""

    def __init__(
        self,
        storage_service: Optional[StorageService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        qdrant_client: Optional[QdrantClient] = None,
    ):
        """
        Initialize visualization service.

        Args:
            storage_service: Storage service for images
            embedding_service: Embedding service for similarity search
            qdrant_client: Qdrant client for vector operations
        """
        self.storage_service = storage_service or StorageService()
        self.embedding_service = embedding_service or EmbeddingService(qdrant_client)
        self.qdrant_client = qdrant_client or QdrantClient()

    async def generate_surgical_preview(
        self,
        image_id: str,
        procedure_id: str,
        patient_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate surgical preview using gemini-2.5-flash-image model.

        Steps:
        1. Retrieve source image from storage
        2. Get procedure details and build prompt
        3. Generate after-surgery image using NanoBanana (gemini-2.5-flash-image)
        4. Store result images in object storage
        5. Generate and store embeddings in Qdrant
        6. Save visualization result to Firestore
        7. Return visualization result

        Args:
            image_id: ID of the uploaded source image
            procedure_id: ID of the surgical procedure
            patient_id: Optional patient profile ID

        Returns:
            Dictionary containing visualization result

        Raises:
            VisualizationError: If visualization generation fails
        """
        try:
            logger.info(
                f"Generating surgical preview for image {image_id}, "
                f"procedure {procedure_id}"
            )

            # Step 1: Retrieve source image from storage
            # First, get image metadata from Firestore to get the correct file extension
            from app.db.firestore_models import get_document
            db = get_db()
            image_data_doc = await get_document(db, Collections.IMAGES, image_id)
            
            if not image_data_doc:
                raise VisualizationError(f"Image {image_id} not found in database")
            
            # Get the file extension from the format
            format_ext_map = {
                "JPEG": ".jpg",
                "PNG": ".png",
                "WEBP": ".webp"
            }
            file_extension = format_ext_map.get(image_data_doc.get("format", "JPEG"), ".jpg")
            
            # Now get the image URL with the correct extension
            before_image_url = self.storage_service.get_image_url(image_id, file_extension)
            if not before_image_url:
                # Fallback: use the URL from the database if available
                before_image_url = image_data_doc.get("url")
                if not before_image_url:
                    raise VisualizationError(f"Image {image_id} not found in storage")

            # Fetch image data for processing
            import httpx
            # Increase timeout for large image downloads
            timeout = httpx.Timeout(60.0, connect=10.0)  # 60s read, 10s connect
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(before_image_url)
                if response.status_code != 200:
                    raise VisualizationError(f"Failed to fetch image: {response.status_code}")
                image_data = response.content

            # Step 2: Get procedure details and build prompt
            procedure = self._get_procedure(procedure_id)
            if not procedure:
                raise VisualizationError(f"Procedure {procedure_id} not found")

            prompt = self._build_prompt(procedure, patient_id)
            logger.info(f"Built prompt: {prompt[:200]}...")

            # Step 3: Generate and upload the after image using NanoBanana (gemini-2.5-flash-image)
            try:
                from app.services.nano_banana_client import NanoBananaClient, NanoBananaAPIError
                nano_banana = NanoBananaClient()
                
                # Use NanoBanana (gemini-2.5-flash-image) to generate the after-surgery image
                logger.info(f"Calling NanoBanana (gemini-2.5-flash-image) to generate surgical visualization...")
                after_image_data = await nano_banana.edit_image(
                    image_data=image_data,
                    prompt=prompt,
                    mime_type="image/jpeg"
                )
                
                # Upload the generated after image to storage
                after_image_file = BytesIO(after_image_data)
                after_image_id, after_image_url = self.storage_service.upload_image(
                    after_image_file,
                    "image/jpeg",
                    f"after_{image_id}.jpg"
                )
                logger.info(f"✅ Successfully generated and uploaded after image using gemini-2.5-flash-image: {after_image_url}")
                
            except NanoBananaAPIError as e:
                logger.error(f"NanoBanana API error: {e}")
                raise VisualizationError(f"Failed to generate visualization: {e}")
            except Exception as e:
                logger.error(f"Failed to generate/upload after image: {e}")
                raise VisualizationError(f"Failed to generate visualization: {e}")

            # Step 5: Generate and store embeddings in Qdrant
            visualization_id = str(uuid.uuid4())
            
            # Determine age range from patient profile if available
            age_range = "unknown"
            if patient_id:
                patient_profile = await self._get_patient_profile(patient_id)
                if patient_profile:
                    age_range = self._calculate_age_range(patient_profile.get("date_of_birth"))

            # Store embedding with metadata
            try:
                # Ensure Qdrant collection exists before storing
                await self.qdrant_client.ensure_collection_exists()
                
                await self.embedding_service.store_embedding(
                    image_data=image_data,
                    visualization_id=visualization_id,
                    procedure_type=procedure["category"],
                    age_range=age_range,
                    outcome_rating=0.8,  # Default rating, would be updated later
                    patient_id=patient_id or "anonymous",
                )
                logger.info(f"Stored embedding for visualization {visualization_id}")
            except Exception as e:
                logger.warning(f"Failed to store embedding: {e}")
                # Don't fail the entire operation if embedding storage fails

            # Step 6: Save visualization result to Firestore
            visualization_data = {
                "id": visualization_id,
                "patient_id": patient_id,
                "procedure_id": procedure_id,
                "procedure_name": procedure["name"],
                "before_image_url": before_image_url,
                "after_image_url": after_image_url,
                "prompt_used": prompt,
                "generated_at": datetime.utcnow(),
                "confidence_score": 0.85,  # Placeholder confidence score
                "metadata": {
                    "model": "gemini-2.5-flash-image",
                    "age_range": age_range,
                },
            }

            # Save to Firestore
            db = get_db()
            db.collection(Collections.VISUALIZATIONS).document(visualization_id).set(
                visualization_data
            )
            logger.info(f"Saved visualization {visualization_id} to Firestore")

            # Step 7: Return visualization result
            return visualization_data

        except VisualizationError:
            raise
        except Exception as e:
            error_msg = str(e) if str(e) else repr(e)
            logger.error(f"Unexpected error generating visualization: {error_msg}", exc_info=True)
            raise VisualizationError(f"Unexpected error: {error_msg}")

    async def get_visualization(self, visualization_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a visualization by ID.

        Args:
            visualization_id: ID of the visualization

        Returns:
            Visualization data or None if not found
        """
        try:
            db = get_db()
            doc = db.collection(Collections.VISUALIZATIONS).document(visualization_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error retrieving visualization {visualization_id}: {e}")
            return None

    async def find_similar_cases(
        self,
        visualization_id: str,
        procedure_type: Optional[str] = None,
        age_range: Optional[str] = None,
        min_outcome_rating: Optional[float] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find similar surgical cases using Qdrant similarity search.

        Args:
            visualization_id: ID of the visualization to find similar cases for
            procedure_type: Filter by procedure type (optional)
            age_range: Filter by age range (optional)
            min_outcome_rating: Minimum outcome rating filter (optional)
            limit: Maximum number of results

        Returns:
            List of similar cases with metadata

        Raises:
            VisualizationError: If search fails
        """
        try:
            logger.info(f"Finding similar cases for visualization {visualization_id}")

            # Get the visualization
            visualization = await self.get_visualization(visualization_id)
            if not visualization:
                raise VisualizationError(f"Visualization {visualization_id} not found")

            # Fetch the before image to generate query embedding
            before_image_url = visualization["before_image_url"]
            
            import httpx
            # Increase timeout for large image downloads
            timeout = httpx.Timeout(60.0, connect=10.0)  # 60s read, 10s connect
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(before_image_url)
                if response.status_code != 200:
                    raise VisualizationError(f"Failed to fetch image: {response.status_code}")
                image_data = response.content

            # Find similar cases using embedding service
            similar_results = await self.embedding_service.find_similar_cases(
                image_data=image_data,
                procedure_type=procedure_type,
                age_range=age_range,
                min_outcome_rating=min_outcome_rating,
                limit=limit,
            )

            # Format results with visualization data
            similar_cases = []
            for result in similar_results:
                payload = result["payload"]
                viz_id = payload.get("visualization_id")
                
                # Get visualization details
                viz_data = await self.get_visualization(viz_id)
                if viz_data:
                    similar_case = {
                        "id": viz_id,
                        "before_image_url": viz_data["before_image_url"],
                        "after_image_url": viz_data["after_image_url"],
                        "procedure_type": payload.get("procedure_type"),
                        "similarity_score": result["score"],
                        "outcome_rating": payload.get("outcome_rating", 0.0),
                        "patient_satisfaction": 4,  # Placeholder
                        "age_range": payload.get("age_range", "unknown"),
                        "anonymized": True,
                    }
                    similar_cases.append(similar_case)

            logger.info(f"Found {len(similar_cases)} similar cases")
            return similar_cases

        except VisualizationError:
            raise
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            raise VisualizationError(f"Failed to find similar cases: {e}")

    def _get_procedure(self, procedure_id: str) -> Optional[Dict[str, Any]]:
        """
        Get procedure details by ID.

        Args:
            procedure_id: Procedure ID

        Returns:
            Procedure data or None if not found
        """
        return get_procedure_by_id(procedure_id)

    def _build_prompt(
        self,
        procedure: Dict[str, Any],
        patient_id: Optional[str] = None,
    ) -> str:
        """
        Build procedure-specific prompt from template.

        Args:
            procedure: Procedure data
            patient_id: Optional patient ID for personalization

        Returns:
            Generated prompt string
        """
        # Get the prompt template
        template = procedure.get("prompt_template", "")
        
        if not template:
            # Fallback to generic prompt
            template = (
                f"Show how this person would look after {procedure['name']}. "
                f"The result should look natural and realistic."
            )
        
        # Replace template placeholders with sensible defaults
        # These placeholders appear in the seed_procedures.py prompt templates
        placeholder_defaults = {
            "{modification_type}": "more refined and balanced",
            "{size_preference}": "natural-looking enhanced",
            "{target_area}": "the affected area",
            "{eyelid_location}": "upper and lower",
            "{augmentation_level}": "moderate",
            "{target_size}": "proportionate",
            "{volume_level}": "natural fullness",
        }
        
        for placeholder, default_value in placeholder_defaults.items():
            template = template.replace(placeholder, default_value)

        # TODO: Add patient-specific customization if patient_id is provided
        # This could include age, skin tone, facial structure considerations

        return template

    async def _get_patient_profile(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get patient profile from Firestore.

        Args:
            patient_id: Patient profile ID

        Returns:
            Patient profile data or None if not found
        """
        try:
            db = get_db()
            doc = db.collection(Collections.PATIENT_PROFILES).document(patient_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error retrieving patient profile {patient_id}: {e}")
            return None

    def _calculate_age_range(self, date_of_birth: Any) -> str:
        """
        Calculate age range from date of birth.

        Args:
            date_of_birth: Date of birth (datetime or string)

        Returns:
            Age range string (e.g., "20-30", "30-40")
        """
        try:
            if isinstance(date_of_birth, str):
                from dateutil import parser
                dob = parser.parse(date_of_birth)
            else:
                dob = date_of_birth

            age = (datetime.utcnow() - dob).days // 365

            # Determine age range
            if age < 20:
                return "under-20"
            elif age < 30:
                return "20-30"
            elif age < 40:
                return "30-40"
            elif age < 50:
                return "40-50"
            elif age < 60:
                return "50-60"
            else:
                return "60-plus"

        except Exception as e:
            logger.warning(f"Error calculating age range: {e}")
            return "unknown"

    async def analyze_similarity_from_urls(
        self,
        ai_image_url: str,
        real_image_url: str,
        procedure_name: str = "the procedure"
    ) -> str:
        """
        Analyze similarity between two images given their URLs.
        
        Args:
            ai_image_url: URL of the AI-generated image
            real_image_url: URL of the real result image
            procedure_name: Name of the procedure for context
            
        Returns:
            AI-generated similarity analysis text
        """
        import httpx
        
        logger.info(f"Analyzing similarity from URLs for {procedure_name}")
        
        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r1 = await client.get(ai_image_url)
            if r1.status_code != 200:
                raise VisualizationError(f"Failed to fetch AI image: {r1.status_code}")
            ai_image_bytes = r1.content
            
            r2 = await client.get(real_image_url)
            if r2.status_code != 200:
                raise VisualizationError(f"Failed to fetch real image: {r2.status_code}")
            real_image_bytes = r2.content

        prompt = (
            f"Analyze the similarity between these two surgical results for {procedure_name}.\n"
            "Image 1 is an AI-predicted outcome.\n"
            "Image 2 is the actual real-world post-surgery result.\n\n"
            "Provide a detailed comparison covering:\n"
            "1. **Similarity Score**: High, Moderate, or Low\n"
            "2. **Anatomical Similarities**: Key matching features\n"
            "3. **Key Differences**: Notable deviations\n"
            "4. **Accuracy Assessment**: How well did the AI predict the outcome?\n\n"
            "Be professional and constructive."
        )

        from app.services.nano_banana_client import NanoBananaClient
        nano_banana = NanoBananaClient()
        
        analysis = await nano_banana.generate_multimodal_analysis(
            prompt=prompt,
            images=[ai_image_bytes, real_image_bytes]
        )
        
        return analysis


# Global visualization service instance
visualization_service = VisualizationService()
