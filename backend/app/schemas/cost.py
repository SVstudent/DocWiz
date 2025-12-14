"""Cost estimation schemas."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class PaymentPlan(BaseModel):
    """Payment plan schema."""
    name: str
    monthly_payment: Decimal
    duration_months: int
    interest_rate: Decimal
    total_paid: Decimal


class CostBreakdownCreate(BaseModel):
    """Cost breakdown creation schema."""
    procedure_id: str
    patient_id: str
    zip_code: str  # For geographic cost variation


class CostBreakdownResponse(BaseModel):
    """Cost breakdown response schema."""
    id: str
    procedure_id: str
    patient_id: str
    surgeon_fee: Decimal
    facility_fee: Decimal
    anesthesia_fee: Decimal
    post_op_care: Decimal
    total_cost: Decimal
    insurance_coverage: Decimal
    patient_responsibility: Decimal
    deductible: Decimal
    copay: Decimal
    out_of_pocket_max: Decimal
    payment_plans: List[PaymentPlan]
    calculated_at: datetime
    data_sources: List[str]
    region: str
    insurance_provider: Optional[str] = None


class InsuranceCoverage(BaseModel):
    """Insurance coverage calculation schema."""
    is_covered: bool
    coverage_rate: Decimal
    estimated_coverage: Decimal
    deductible: Decimal
    copay: Decimal
    out_of_pocket_max: Decimal
    patient_responsibility: Decimal


class CostInfographicRequest(BaseModel):
    """Cost infographic generation request."""
    cost_breakdown_id: str
    format: str = Field(default="png", pattern="^(png|jpeg)$")
