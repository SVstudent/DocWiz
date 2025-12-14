"""Schemas for procedure comparison functionality."""
from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class ComparisonRequest(BaseModel):
    """Request schema for creating a multi-procedure comparison."""
    
    source_image_id: str = Field(..., description="ID of the source image to use for all comparisons")
    procedure_ids: List[str] = Field(..., min_length=2, description="List of procedure IDs to compare (minimum 2)")
    patient_id: Optional[str] = Field(None, description="Optional patient profile ID")


class ProcedureComparisonData(BaseModel):
    """Comparison data for a single procedure."""
    
    procedure_id: str = Field(..., description="Procedure ID")
    procedure_name: str = Field(..., description="Procedure name")
    visualization_id: str = Field(..., description="Generated visualization ID")
    before_image_url: str = Field(..., description="Before image URL")
    after_image_url: str = Field(..., description="After image URL")
    cost: float = Field(..., description="Estimated total cost")
    recovery_days: int = Field(..., description="Recovery time in days")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")


class ComparisonResult(BaseModel):
    """Response schema for comparison result."""
    
    id: str = Field(..., description="Unique identifier for the comparison")
    source_image_id: str = Field(..., description="Source image ID used for all visualizations")
    patient_id: Optional[str] = Field(None, description="Patient profile ID if provided")
    procedures: List[ProcedureComparisonData] = Field(..., description="List of procedure comparison data")
    cost_differences: Dict[str, float] = Field(..., description="Cost differences between procedures")
    recovery_differences: Dict[str, int] = Field(..., description="Recovery time differences")
    risk_differences: Dict[str, str] = Field(..., description="Risk level differences")
    created_at: datetime = Field(..., description="Comparison creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ComparisonResponse(BaseModel):
    """Response schema for retrieving a comparison."""
    
    comparison: ComparisonResult = Field(..., description="The comparison result")
