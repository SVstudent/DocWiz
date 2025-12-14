"""Pydantic schemas for procedure API responses."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProcedureResponse(BaseModel):
    """Response schema for a single procedure."""
    id: str
    name: str
    category: str
    description: str
    typical_cost_min: float
    typical_cost_max: float
    recovery_days: int
    risk_level: str
    cpt_codes: List[str]
    icd10_codes: List[str]
    prompt_template: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProcedureListResponse(BaseModel):
    """Response schema for list of procedures."""
    procedures: List[ProcedureResponse]
    total: int


class CategoryListResponse(BaseModel):
    """Response schema for list of categories."""
    categories: List[str]
    total: int


class ProcedureDisplayResponse(BaseModel):
    """Response schema for displaying procedure to patient.
    
    This schema includes only the information needed for patient display,
    following Requirements 1.2 which specifies that procedure display must
    include description, typical recovery time, and risk factors.
    """
    id: str
    name: str
    category: str
    description: str
    recovery_days: int
    risk_level: str
    cost_range: dict = Field(
        description="Cost range with min and max values"
    )
    
    class Config:
        from_attributes = True
