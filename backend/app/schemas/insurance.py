"""Insurance documentation schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class ProviderInfo(BaseModel):
    """Healthcare provider information."""
    name: str
    npi: str
    address: str
    phone: str
    specialty: str


class PreAuthFormCreate(BaseModel):
    """Pre-authorization form creation request."""
    procedure_id: str
    patient_id: str
    cost_breakdown_id: Optional[str] = None
    provider_info: Optional[ProviderInfo] = None





class FacilityInfo(BaseModel):
    """Service facility information."""
    name: str = "DocWiz Surgical Center"
    npi: str = "1923456789"
    address: str
    place_of_service_code: str = "24"  # Ambulatory Surgical Center


class ReferringProvider(BaseModel):
    """Referring provider information."""
    name: Optional[str] = None
    npi: Optional[str] = None


class DiagnosisInfo(BaseModel):
    """Diagnosis information."""
    icd10_code: str
    description: Optional[str] = None
    type: str = "Principal"  # Principal, Admitting, etc.


class ServiceLineItem(BaseModel):
    """Service line item details."""
    procedure_code: str
    modifiers: List[str] = []
    description: str
    quantity: float = 1.0
    unit_price: float
    total_price: float
    diagnosis_pointers: List[int] = [1]  # Points to diagnosis codes (1, 2, 3, 4)
    service_date: datetime


class ClaimHeader(BaseModel):
    """Insurance claim header information."""
    claim_type: str = "Professional"  # Professional, Institutional
    place_of_service: str = "24"      # 11=Office, 21=Inpatient, 22=Outpatient, 24=ASC
    prior_authorization_number: Optional[str] = None
    referral_number: Optional[str] = None
    claim_frequency_code: str = "1"   # 1=Original, 7=Replacement, 8=Void


class InsuranceValidationRequest(BaseModel):
    """Insurance validation request."""
    provider: str
    policy_number: str
    group_number: Optional[str] = None


class InsuranceValidationResponse(BaseModel):
    """Insurance validation response."""
    is_valid: bool
    provider: str
    message: str
    supported_procedures: Optional[List[str]] = None


class PreAuthFormResponse(BaseModel):
    """Pre-authorization form response."""
    id: str
    patient_id: str
    procedure_id: str
    cost_breakdown_id: Optional[str] = None
    
    # Claim Header
    claim_header: Optional[ClaimHeader] = None
    
    # Diagnosis Codes
    cpt_codes: List[str]
    icd10_codes: List[str]
    diagnosis_details: List[DiagnosisInfo] = []
    
    # Service Lines
    service_lines: List[ServiceLineItem] = []
    
    # Provider & Facility
    provider_info: ProviderInfo
    facility_info: Optional[FacilityInfo] = None
    referring_provider: Optional[ReferringProvider] = None
    
    # Clinical
    medical_justification: str
    
    # Output
    pdf_url: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    generated_at: datetime

    class Config:
        from_attributes = True
