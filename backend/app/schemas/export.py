"""Schemas for export API."""
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """Request schema for creating an export."""
    
    patient_id: str = Field(..., description="Patient profile ID")
    format: Literal["pdf", "png", "jpeg", "json"] = Field(..., description="Export format")
    shareable: bool = Field(default=False, description="Whether to create shareable version (removes sensitive data)")
    include_visualizations: bool = Field(default=True, description="Include visualization results")
    include_cost_estimates: bool = Field(default=True, description="Include cost estimates")
    include_comparisons: bool = Field(default=True, description="Include comparison sets")
    visualization_ids: Optional[List[str]] = Field(None, description="Specific visualization IDs to include (all if None)")
    cost_breakdown_ids: Optional[List[str]] = Field(None, description="Specific cost breakdown IDs to include (all if None)")
    comparison_ids: Optional[List[str]] = Field(None, description="Specific comparison IDs to include (all if None)")


class ExportMetadata(BaseModel):
    """Metadata for an export."""
    
    id: str = Field(..., description="Unique export identifier")
    patient_id: str = Field(..., description="Patient profile ID")
    patient_name: str = Field(..., description="Patient name")
    format: str = Field(..., description="Export format")
    shareable: bool = Field(..., description="Whether this is a shareable export")
    created_at: datetime = Field(..., description="Export creation timestamp")
    file_size_bytes: Optional[int] = Field(None, description="File size in bytes")
    download_url: Optional[str] = Field(None, description="Download URL")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp for download URL")


class ExportResponse(BaseModel):
    """Response schema for export creation."""
    
    id: str = Field(..., description="Unique export identifier")
    patient_id: str = Field(..., description="Patient profile ID")
    patient_name: str = Field(..., description="Patient name")
    format: str = Field(..., description="Export format")
    shareable: bool = Field(..., description="Whether this is a shareable export")
    created_at: datetime = Field(..., description="Export creation timestamp")
    status: Literal["pending", "processing", "completed", "failed"] = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL (available when status is completed)")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")


class ExportData(BaseModel):
    """Complete export data structure."""
    
    export_id: str
    patient_name: str
    generated_at: datetime
    shareable: bool
    visualizations: List[Dict[str, Any]] = Field(default_factory=list)
    cost_estimates: List[Dict[str, Any]] = Field(default_factory=list)
    comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    disclaimer: str = Field(
        default="MEDICAL DISCLAIMER: This report is for informational purposes only and does not constitute medical advice. "
        "All surgical visualizations are AI-generated predictions and may not reflect actual surgical outcomes. "
        "Cost estimates are approximate and subject to change. Always consult with qualified medical professionals "
        "before making any healthcare decisions."
    )
