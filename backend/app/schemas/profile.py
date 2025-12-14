"""Patient profile schemas."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class LocationCreate(BaseModel):
    """Location creation schema."""
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "USA"
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Validate zip code format (US 5-digit or 5+4 format)."""
        # Remove any spaces or hyphens
        v = v.replace(' ', '').replace('-', '')
        
        # Check if it's 5 digits or 9 digits
        if len(v) == 5 and v.isdigit():
            return v[:5]  # Return 5-digit format
        elif len(v) == 9 and v.isdigit():
            return f"{v[:5]}-{v[5:]}"  # Return 5+4 format
        else:
            raise ValueError('Zip code must be 5 or 9 digits')


class LocationResponse(LocationCreate):
    """Location response schema."""
    pass


class InsuranceInfoCreate(BaseModel):
    """Insurance information creation schema."""
    provider: str
    policy_number: str  # Will be encrypted before storage
    group_number: Optional[str] = None
    plan_type: Optional[str] = None
    coverage_details: Optional[Dict[str, Any]] = None


class InsuranceInfoResponse(BaseModel):
    """Insurance information response schema."""
    provider: str
    policy_number: str  # Decrypted for display
    group_number: Optional[str] = None
    plan_type: Optional[str] = None
    coverage_details: Optional[Dict[str, Any]] = None


class PatientProfileCreate(BaseModel):
    """Patient profile creation schema."""
    name: str
    date_of_birth: date
    location: LocationCreate
    insurance_info: InsuranceInfoCreate
    medical_history: Optional[str] = None


class PatientProfileUpdate(BaseModel):
    """Patient profile update schema."""
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    location: Optional[LocationCreate] = None
    insurance_info: Optional[InsuranceInfoCreate] = None
    medical_history: Optional[str] = None


class PatientProfileResponse(BaseModel):
    """Patient profile response schema."""
    id: str
    user_id: str
    name: str
    date_of_birth: date
    location: LocationResponse
    insurance_info: InsuranceInfoResponse
    medical_history: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime


class ProfileVersionHistoryResponse(BaseModel):
    """Profile version history response schema."""
    id: str
    profile_id: str
    version: int
    data: Dict[str, Any]
    created_at: datetime


class ProfileValidationResult(BaseModel):
    """Profile validation result schema."""
    is_valid: bool
    missing_fields: List[str] = Field(default_factory=list)
    invalid_fields: Dict[str, str] = Field(default_factory=dict)
