"""Schemas for surgical visualization API."""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class VisualizationRequest(BaseModel):
    """Request schema for generating surgical visualization."""
    
    image_id: str = Field(..., description="ID of the uploaded source image")
    procedure_id: str = Field(..., description="ID of the surgical procedure")
    patient_id: Optional[str] = Field(None, description="Optional patient profile ID")


class VisualizationResult(BaseModel):
    """Response schema for visualization result."""
    
    id: str = Field(..., description="Unique identifier for the visualization")
    patient_id: Optional[str] = Field(None, description="Patient profile ID if provided")
    procedure_id: str = Field(..., description="Procedure ID")
    procedure_name: str = Field(..., description="Procedure name")
    before_image_url: str = Field(..., description="URL of the before image")
    after_image_url: str = Field(..., description="URL of the generated after image")
    prompt_used: str = Field(..., description="Prompt used for generation")
    generated_at: datetime = Field(..., description="Generation timestamp")
    confidence_score: float = Field(..., description="Confidence score (0.0-1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SimilarCase(BaseModel):
    """Schema for similar case result."""
    
    id: str = Field(..., description="Visualization ID")
    before_image_url: str = Field(..., description="Before image URL")
    after_image_url: str = Field(..., description="After image URL")
    procedure_type: str = Field(..., description="Procedure type")
    similarity_score: float = Field(..., description="Similarity score (0.0-1.0)")
    outcome_rating: float = Field(..., description="Outcome quality rating (0.0-1.0)")
    patient_satisfaction: int = Field(..., description="Patient satisfaction score (1-5)")
    age_range: str = Field(..., description="Patient age range (e.g., '20-30')")
    anonymized: bool = Field(default=True, description="Whether data is anonymized")


class SimilarCasesRequest(BaseModel):
    """Request schema for finding similar cases."""
    
    visualization_id: str = Field(..., description="ID of the visualization to find similar cases for")
    procedure_type: Optional[str] = Field(None, description="Filter by procedure type")
    age_range: Optional[str] = Field(None, description="Filter by age range")
    min_outcome_rating: Optional[float] = Field(None, description="Minimum outcome rating filter")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")


class SimilarCasesResponse(BaseModel):
    """Response schema for similar cases search."""
    
    query_visualization_id: str = Field(..., description="ID of the query visualization")
    similar_cases: List[SimilarCase] = Field(..., description="List of similar cases")
    total_found: int = Field(..., description="Total number of similar cases found")
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Filters that were applied")


class VisualizationListResponse(BaseModel):
    """Response schema for list of visualizations."""
    
    visualizations: List[VisualizationResult]
    total: int
