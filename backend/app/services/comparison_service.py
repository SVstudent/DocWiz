"""Service for multi-procedure comparison functionality."""
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.services.visualization_service import VisualizationService, VisualizationError
from app.services.procedure_service import ProcedureService
from app.db.base import get_db, Collections

logger = logging.getLogger(__name__)


class ComparisonError(Exception):
    """Base exception for comparison errors."""
    pass


class ComparisonService:
    """Service for creating and managing multi-procedure comparisons."""

    def __init__(
        self,
        visualization_service: Optional[VisualizationService] = None,
        procedure_service: Optional[ProcedureService] = None,
    ):
        """
        Initialize comparison service.

        Args:
            visualization_service: Service for generating visualizations
            procedure_service: Service for retrieving procedure data
        """
        self.visualization_service = visualization_service or VisualizationService()
        self.procedure_service = procedure_service

    async def create_comparison(
        self,
        source_image_id: str,
        procedure_ids: List[str],
        patient_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a multi-procedure comparison.

        This method:
        1. Validates that all procedures exist
        2. Generates visualizations for each procedure using the same source image
        3. Calculates cost, recovery time, and risk differences
        4. Stores the comparison set with metadata
        5. Returns the complete comparison result

        Args:
            source_image_id: ID of the source image to use for all comparisons
            procedure_ids: List of procedure IDs to compare (minimum 2)
            patient_id: Optional patient profile ID

        Returns:
            Dictionary containing comparison result with all procedure data

        Raises:
            ComparisonError: If comparison creation fails
        """
        try:
            logger.info(
                f"Creating comparison for image {source_image_id} "
                f"with {len(procedure_ids)} procedures"
            )

            # Validate minimum procedures
            if len(procedure_ids) < 2:
                raise ComparisonError("At least 2 procedures required for comparison")

            # Step 1: Validate that all procedures exist and fetch their data
            procedures_data = []
            for proc_id in procedure_ids:
                if self.procedure_service:
                    procedure = await self.procedure_service.get_procedure_by_id(proc_id)
                    if not procedure:
                        raise ComparisonError(f"Procedure {proc_id} not found")
                    # Convert Pydantic model to dict
                    proc_dict = procedure.model_dump()
                else:
                    # Fallback to seed data
                    from app.db.seed_procedures import get_procedure_by_id
                    procedure = get_procedure_by_id(proc_id)
                    if not procedure:
                        raise ComparisonError(f"Procedure {proc_id} not found")
                    proc_dict = procedure
                
                procedures_data.append(proc_dict)

            logger.info(f"Validated {len(procedures_data)} procedures")

            # Step 2: Generate visualizations for each procedure using the same source image
            comparison_procedures = []
            for procedure in procedures_data:
                try:
                    # Generate visualization
                    visualization = await self.visualization_service.generate_surgical_preview(
                        image_id=source_image_id,
                        procedure_id=procedure["id"],
                        patient_id=patient_id,
                    )

                    # Extract cost from procedure data
                    # Use the midpoint of the cost range
                    cost_range = procedure.get("typical_cost_range", [0, 0])
                    if isinstance(cost_range, (list, tuple)) and len(cost_range) == 2:
                        estimated_cost = (cost_range[0] + cost_range[1]) / 2
                    else:
                        estimated_cost = 0.0

                    # Build procedure comparison data
                    proc_comparison = {
                        "procedure_id": procedure["id"],
                        "procedure_name": procedure["name"],
                        "visualization_id": visualization["id"],
                        "before_image_url": visualization["before_image_url"],
                        "after_image_url": visualization["after_image_url"],
                        "cost": estimated_cost,
                        "recovery_days": procedure.get("recovery_days", 0),
                        "risk_level": procedure.get("risk_level", "unknown"),
                    }
                    comparison_procedures.append(proc_comparison)
                    logger.info(f"Generated visualization for procedure {procedure['id']}")

                except VisualizationError as e:
                    logger.error(f"Failed to generate visualization for {procedure['id']}: {e}")
                    raise ComparisonError(
                        f"Failed to generate visualization for {procedure['name']}: {e}"
                    )

            # Step 3: Calculate cost, recovery time, and risk differences
            cost_differences = self._calculate_cost_differences(comparison_procedures)
            recovery_differences = self._calculate_recovery_differences(comparison_procedures)
            risk_differences = self._calculate_risk_differences(comparison_procedures)

            logger.info("Calculated comparison differences")

            # Step 4: Store the comparison set with metadata
            comparison_id = str(uuid.uuid4())
            comparison_data = {
                "id": comparison_id,
                "source_image_id": source_image_id,
                "patient_id": patient_id,
                "procedures": comparison_procedures,
                "cost_differences": cost_differences,
                "recovery_differences": recovery_differences,
                "risk_differences": risk_differences,
                "created_at": datetime.utcnow(),
                "metadata": {
                    "procedure_count": len(comparison_procedures),
                    "procedure_ids": procedure_ids,
                },
            }

            # Save to Firestore
            db = get_db()
            db.collection(Collections.COMPARISONS).document(comparison_id).set(
                comparison_data
            )
            logger.info(f"Saved comparison {comparison_id} to Firestore")

            # Step 5: Return the complete comparison result
            return comparison_data

        except ComparisonError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating comparison: {e}")
            raise ComparisonError(f"Unexpected error: {e}")

    async def get_comparison(self, comparison_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a comparison by ID.

        Args:
            comparison_id: ID of the comparison

        Returns:
            Comparison data or None if not found
        """
        try:
            db = get_db()
            doc = db.collection(Collections.COMPARISONS).document(comparison_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error retrieving comparison {comparison_id}: {e}")
            return None

    def _calculate_cost_differences(
        self, procedures: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate cost differences between procedures.

        Args:
            procedures: List of procedure comparison data

        Returns:
            Dictionary mapping procedure pairs to cost differences
        """
        differences = {}
        
        for i, proc1 in enumerate(procedures):
            for proc2 in procedures[i + 1:]:
                key = f"{proc1['procedure_name']}_vs_{proc2['procedure_name']}"
                diff = abs(proc1["cost"] - proc2["cost"])
                differences[key] = diff

        return differences

    def _calculate_recovery_differences(
        self, procedures: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Calculate recovery time differences between procedures.

        Args:
            procedures: List of procedure comparison data

        Returns:
            Dictionary mapping procedure pairs to recovery time differences (in days)
        """
        differences = {}
        
        for i, proc1 in enumerate(procedures):
            for proc2 in procedures[i + 1:]:
                key = f"{proc1['procedure_name']}_vs_{proc2['procedure_name']}"
                diff = abs(proc1["recovery_days"] - proc2["recovery_days"])
                differences[key] = diff

        return differences

    def _calculate_risk_differences(
        self, procedures: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Calculate risk level differences between procedures.

        Args:
            procedures: List of procedure comparison data

        Returns:
            Dictionary mapping procedure pairs to risk level comparison strings
        """
        differences = {}
        
        # Risk level ordering
        risk_order = {"low": 1, "medium": 2, "high": 3, "unknown": 0}
        
        for i, proc1 in enumerate(procedures):
            for proc2 in procedures[i + 1:]:
                key = f"{proc1['procedure_name']}_vs_{proc2['procedure_name']}"
                
                risk1 = proc1["risk_level"].lower()
                risk2 = proc2["risk_level"].lower()
                
                level1 = risk_order.get(risk1, 0)
                level2 = risk_order.get(risk2, 0)
                
                if level1 == level2:
                    diff_str = f"Same risk level ({risk1})"
                elif level1 > level2:
                    diff_str = f"{proc1['procedure_name']} has higher risk ({risk1} vs {risk2})"
                else:
                    diff_str = f"{proc2['procedure_name']} has higher risk ({risk2} vs {risk1})"
                
                differences[key] = diff_str

        return differences


# Global comparison service instance
comparison_service = ComparisonService()

