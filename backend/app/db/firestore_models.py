"""Firestore data models and helper functions.

Since Firestore is a NoSQL document database, we don't use SQLAlchemy models.
Instead, we define Pydantic models for data validation and helper functions
for CRUD operations.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from google.cloud.firestore_v1 import Client
from pydantic import BaseModel, Field

from app.db.base import Collections


def generate_id() -> str:
    """Generate a unique ID for Firestore documents."""
    return str(uuid.uuid4())


# Pydantic models for data validation

class UserModel(BaseModel):
    """User model for authentication."""
    id: str = Field(default_factory=generate_id)
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LocationModel(BaseModel):
    """Location information."""
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "USA"


class InsuranceInfoModel(BaseModel):
    """Insurance information."""
    provider: str
    encrypted_policy_number: str
    group_number: Optional[str] = None
    plan_type: Optional[str] = None
    coverage_details: Optional[Dict[str, Any]] = None


class PatientProfileModel(BaseModel):
    """Patient profile model."""
    id: str = Field(default_factory=generate_id)
    user_id: str
    name: str
    date_of_birth: datetime
    location: LocationModel
    insurance_info: InsuranceInfoModel
    encrypted_medical_history: Optional[str] = None
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProfileVersionHistoryModel(BaseModel):
    """Profile version history."""
    id: str = Field(default_factory=generate_id)
    profile_id: str
    version: int
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProcedureModel(BaseModel):
    """Surgical procedure model."""
    id: str = Field(default_factory=generate_id)
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VisualizationResultModel(BaseModel):
    """Surgical visualization result model."""
    id: str = Field(default_factory=generate_id)
    patient_id: str
    procedure_id: str
    procedure_name: Optional[str] = None
    before_image_url: str
    after_image_url: str
    prompt_used: str
    confidence_score: Optional[float] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentPlanModel(BaseModel):
    """Payment plan information."""
    name: str
    monthly_payment: float
    duration_months: int
    interest_rate: float
    total_paid: float


class CostBreakdownModel(BaseModel):
    """Cost breakdown model."""
    id: str = Field(default_factory=generate_id)
    procedure_id: str
    patient_id: str
    surgeon_fee: float
    facility_fee: float
    anesthesia_fee: float
    post_op_care: float
    total_cost: float
    insurance_coverage: Optional[float] = None
    patient_responsibility: Optional[float] = None
    deductible: Optional[float] = None
    copay: Optional[float] = None
    out_of_pocket_max: Optional[float] = None
    payment_plans: Optional[List[PaymentPlanModel]] = None
    data_sources: Optional[List[str]] = None
    region: Optional[str] = None
    insurance_provider: Optional[str] = None
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class ProviderInfoModel(BaseModel):
    """Healthcare provider information."""
    name: str
    npi: str
    address: str
    phone: str
    specialty: str



class FacilityInfoModel(BaseModel):
    """Service facility information."""
    name: str = "DocWiz Surgical Center"
    npi: str = "1923456789"
    address: str
    place_of_service_code: str = "24"  # Ambulatory Surgical Center


class ReferringProviderModel(BaseModel):
    """Referring provider information."""
    name: Optional[str] = None
    npi: Optional[str] = None


class DiagnosisInfoModel(BaseModel):
    """Diagnosis information."""
    icd10_code: str
    description: Optional[str] = None
    type: str = "Principal"  # Principal, Admitting, etc.


class ServiceLineItemModel(BaseModel):
    """Service line item details."""
    procedure_code: str
    modifiers: List[str] = []
    description: str
    quantity: float = 1.0
    unit_price: float
    total_price: float
    diagnosis_pointers: List[int] = [1]  # Points to diagnosis codes (1, 2, 3, 4)
    service_date: datetime


class ClaimHeaderModel(BaseModel):
    """Insurance claim header information."""
    claim_type: str = "Professional"
    place_of_service: str = "24"
    prior_authorization_number: Optional[str] = None
    referral_number: Optional[str] = None
    claim_frequency_code: str = "1"


class PreAuthFormModel(BaseModel):
    """Pre-authorization form model."""
    id: str = Field(default_factory=generate_id)
    patient_id: str
    procedure_id: str
    cost_breakdown_id: Optional[str] = None
    
    # Claim Header
    claim_header: Optional[ClaimHeaderModel] = None
    
    # Diagnosis Codes
    cpt_codes: List[str]
    icd10_codes: List[str]
    diagnosis_details: List[DiagnosisInfoModel] = []
    
    # Service Lines
    service_lines: List[ServiceLineItemModel] = []
    
    # Provider & Facility
    provider_info: ProviderInfoModel
    facility_info: Optional[FacilityInfoModel] = None
    referring_provider: Optional[ReferringProviderModel] = None

    medical_justification: str
    pdf_url: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ImageModel(BaseModel):
    """Uploaded image model."""
    id: str = Field(default_factory=generate_id)
    user_id: str
    url: str
    width: int
    height: int
    format: str
    size_bytes: int
    original_filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ComparisonModel(BaseModel):
    """Procedure comparison model."""
    id: str = Field(default_factory=generate_id)
    patient_id: str
    source_image_id: str
    procedure_ids: List[str]
    visualization_ids: List[str]
    cost_breakdown_ids: List[str]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Alias for consistency with other parts of the codebase
ComparisonSetModel = ComparisonModel


# Helper functions for Firestore operations

async def create_document(db: Client, collection: str, data: BaseModel) -> str:
    """Create a document in Firestore."""
    doc_dict = data.model_dump(mode='json')
    # Convert datetime objects to Firestore timestamps
    for key, value in doc_dict.items():
        if isinstance(value, datetime):
            doc_dict[key] = value
    
    doc_id = doc_dict.get('id', generate_id())
    db.collection(collection).document(doc_id).set(doc_dict)
    return doc_id


async def get_document(db: Client, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """Get a document from Firestore."""
    doc_ref = db.collection(collection).document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None


async def update_document(db: Client, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
    """Update a document in Firestore."""
    data['updated_at'] = datetime.utcnow()
    db.collection(collection).document(doc_id).update(data)


async def delete_document(db: Client, collection: str, doc_id: str) -> None:
    """Delete a document from Firestore."""
    db.collection(collection).document(doc_id).delete()


async def query_documents(
    db: Client,
    collection: str,
    filters: Optional[List[tuple]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Query documents from Firestore.
    
    Args:
        db: Firestore client
        collection: Collection name
        filters: List of tuples (field, operator, value) for filtering
        order_by: Field name to order by
        limit: Maximum number of documents to return
    
    Returns:
        List of document dictionaries
    """
    query = db.collection(collection)
    
    if filters:
        for field, operator, value in filters:
            query = query.where(field, operator, value)
    
    if order_by:
        query = query.order_by(order_by)
    
    if limit:
        query = query.limit(limit)
    
    docs = query.stream()
    return [doc.to_dict() for doc in docs]
