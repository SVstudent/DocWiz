# Design Document

## Overview

DocWiz is a full-stack web application that combines AI-powered surgical visualization with comprehensive cost estimation and insurance planning. The system follows a clean, minimalist design philosophy - "surgically effective" - with precise, purposeful interfaces that prioritize clarity and user confidence.

The architecture integrates multiple AI services:
- **Google Gemini 2.5 Flash Image**: Photorealistic surgical preview generation with region-specific editing
- **Google Nano Banana**: Natural language generation for insurance documentation and medical explanations
- **Freepik Studio**: Enhanced image/video generation and creative assets
- **Qdrant**: Vector embeddings and similarity search for case matching

The frontend uses React with Next.js for server-side rendering and optimal performance, while the backend leverages FastAPI for high-performance async API operations. All patient data is encrypted and HIPAA-compliant.

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js/React UI]
        State[State Management - Zustand]
        Upload[Image Upload Component]
        Viz[Visualization Viewer]
        Cost[Cost Dashboard]
        Compare[Comparison Tool]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server]
        Auth[Authentication Service]
        Profile[Profile Service]
        VizService[Visualization Service]
        CostService[Cost Estimation Service]
        Export[Export Service]
    end
    
    subgraph "AI Services"
        Gemini[Gemini 2.5 Flash Image]
        Nano[Nano Banana]
        Freepik[Freepik Studio API]
    end
    
    subgraph "Data Layer"
        Qdrant[Qdrant Vector DB]
        Postgres[(PostgreSQL)]
        S3[Object Storage]
    end
    
    UI --> API
    Upload --> VizService
    Viz --> VizService
    Cost --> CostService
    Compare --> VizService
    
    VizService --> Gemini
    VizService --> Freepik
    VizService --> Qdrant
    CostService --> Nano
    Export --> Nano
    
    Profile --> Postgres
    VizService --> S3
    VizService --> Qdrant
    Auth --> Postgres
```

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS (for clean, surgical design system)
- Zustand (lightweight state management)
- React Query (server state management)
- Framer Motion (smooth transitions)

**Backend:**
- Python 3.11+
- FastAPI
- Pydantic (data validation)
- SQLAlchemy (ORM)
- Alembic (migrations)
- Celery (async task processing)
- Redis (caching and task queue)

**AI Integration:**
- Google Gemini API (2.5 Flash Image)
- Google Nano Banana API
- Freepik API
- Qdrant Python Client

**Data Storage:**
- PostgreSQL (patient profiles, procedures, cost data)
- Qdrant (vector embeddings for similarity search)
- AWS S3 / CloudFlare R2 (image storage)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt (SSL)

## Components and Interfaces

### Frontend Components

#### 1. Image Upload Component
```typescript
interface ImageUploadProps {
  onUploadComplete: (imageId: string, imageUrl: string) => void;
  maxSizeMB: number;
  acceptedFormats: string[];
}

interface UploadedImage {
  id: string;
  url: string;
  width: number;
  height: number;
  format: string;
  uploadedAt: Date;
}
```

**Responsibilities:**
- Validate image format (JPEG, PNG, WebP)
- Check file size (max 10MB)
- Display upload progress
- Preview uploaded image
- Handle upload errors gracefully

#### 2. Procedure Selector Component
```typescript
interface ProcedureSelectorProps {
  onProcedureSelect: (procedure: Procedure) => void;
  selectedProcedures: Procedure[];
  multiSelect: boolean;
}

interface Procedure {
  id: string;
  name: string;
  category: string;
  description: string;
  typicalCost: number;
  recoveryDays: number;
  riskLevel: 'low' | 'medium' | 'high';
}
```

#### 3. Visualization Viewer Component
```typescript
interface VisualizationViewerProps {
  beforeImage: string;
  afterImage: string;
  procedure: Procedure;
  onSave: () => void;
  onRegenerate: () => void;
}

interface VisualizationResult {
  id: string;
  beforeImageUrl: string;
  afterImageUrl: string;
  procedureId: string;
  generatedAt: Date;
  prompt: string;
  confidence: number;
}
```

**Features:**
- Side-by-side before/after view
- Slider comparison tool
- Zoom and pan controls (synchronized)
- Save to profile
- Regenerate with adjustments

#### 4. Cost Dashboard Component
```typescript
interface CostDashboardProps {
  procedure: Procedure;
  patientProfile: PatientProfile;
  onExport: (format: 'pdf' | 'png' | 'json') => void;
}

interface CostBreakdown {
  surgeonFee: number;
  facilityFee: number;
  anesthesiaFee: number;
  postOpCare: number;
  total: number;
  insuranceCoverage: number;
  deductible: number;
  copay: number;
  outOfPocket: number;
  paymentPlans: PaymentPlan[];
}
```

**Features:**
- Visual cost breakdown (chart)
- Insurance coverage calculator
- Payment plan options
- Export as infographic (PNG/JPEG)
- Export as detailed PDF

#### 5. Comparison Tool Component
```typescript
interface ComparisonToolProps {
  procedures: Procedure[];
  sourceImage: string;
  onCompare: (procedures: Procedure[]) => void;
}

interface ComparisonResult {
  procedures: Procedure[];
  visualizations: VisualizationResult[];
  costComparison: CostBreakdown[];
  recoveryComparison: number[];
  riskComparison: string[];
}
```

### Backend Services

#### 1. Visualization Service
```python
class VisualizationService:
    def __init__(
        self,
        gemini_client: GeminiClient,
        freepik_client: FreepikClient,
        qdrant_client: QdrantClient,
        storage_service: StorageService
    ):
        pass
    
    async def generate_surgical_preview(
        self,
        image_id: str,
        procedure: Procedure,
        patient_profile: PatientProfile
    ) -> VisualizationResult:
        """
        Generate surgical preview using Gemini 2.5 Flash Image.
        
        Steps:
        1. Retrieve source image from storage
        2. Build procedure-specific prompt
        3. Call Gemini API with image + prompt
        4. Validate anatomical plausibility
        5. Store result and generate embedding
        6. Return visualization result
        """
        pass
    
    async def generate_embedding(
        self,
        image_url: str
    ) -> List[float]:
        """Generate vector embedding for similarity search."""
        pass
    
    async def find_similar_cases(
        self,
        embedding: List[float],
        procedure_type: str,
        limit: int = 10
    ) -> List[SimilarCase]:
        """Find similar surgical cases using Qdrant."""
        pass
```

#### 2. Cost Estimation Service
```python
class CostEstimationService:
    def __init__(
        self,
        nano_banana_client: NanoBananaClient,
        pricing_db: PricingDatabase
    ):
        pass
    
    async def calculate_cost_breakdown(
        self,
        procedure: Procedure,
        patient_profile: PatientProfile
    ) -> CostBreakdown:
        """
        Calculate comprehensive cost breakdown.
        
        Factors:
        - Geographic location (zip code)
        - Insurance provider and plan
        - Procedure complexity
        - Surgeon experience level
        - Facility type
        """
        pass
    
    async def generate_cost_infographic(
        self,
        cost_breakdown: CostBreakdown,
        format: str = 'png'
    ) -> bytes:
        """Generate visual cost breakdown using Freepik."""
        pass
    
    async def calculate_insurance_coverage(
        self,
        procedure: Procedure,
        insurance_info: InsuranceInfo
    ) -> InsuranceCoverage:
        """Calculate estimated insurance coverage."""
        pass
```

#### 3. Insurance Documentation Service
```python
class InsuranceDocService:
    def __init__(
        self,
        nano_banana_client: NanoBananaClient
    ):
        pass
    
    async def generate_preauth_form(
        self,
        procedure: Procedure,
        patient_profile: PatientProfile,
        cost_breakdown: CostBreakdown
    ) -> PreAuthForm:
        """
        Generate pre-authorization form using Nano Banana.
        
        Includes:
        - CPT/ICD-10 codes
        - Medical necessity justification
        - Cost breakdown
        - Provider information
        """
        pass
    
    async def generate_medical_justification(
        self,
        procedure: Procedure,
        patient_history: str
    ) -> str:
        """Generate professional medical necessity text."""
        pass
```

#### 4. Profile Service
```python
class ProfileService:
    def __init__(
        self,
        db: Database,
        encryption_service: EncryptionService
    ):
        pass
    
    async def create_profile(
        self,
        profile_data: PatientProfileCreate
    ) -> PatientProfile:
        """Create encrypted patient profile."""
        pass
    
    async def update_profile(
        self,
        profile_id: str,
        updates: PatientProfileUpdate
    ) -> PatientProfile:
        """Update profile with version history."""
        pass
    
    async def validate_insurance(
        self,
        insurance_info: InsuranceInfo
    ) -> bool:
        """Validate insurance provider and policy."""
        pass
```

#### 5. Export Service
```python
class ExportService:
    def __init__(
        self,
        nano_banana_client: NanoBananaClient,
        pdf_generator: PDFGenerator
    ):
        pass
    
    async def export_comprehensive_report(
        self,
        patient_id: str,
        visualization_ids: List[str],
        format: str = 'pdf'
    ) -> bytes:
        """
        Export comprehensive surgical analysis report.
        
        Includes:
        - All visualizations
        - Cost breakdowns
        - Comparison analysis
        - Insurance documentation
        - Disclaimers
        """
        pass
    
    async def export_shareable_version(
        self,
        report_data: ReportData
    ) -> bytes:
        """Export with sensitive data removed."""
        pass
```

## Data Models

### Patient Profile
```python
class PatientProfile(BaseModel):
    id: str
    user_id: str
    name: str
    date_of_birth: date
    location: Location
    insurance_info: InsuranceInfo
    medical_history: Optional[str]
    created_at: datetime
    updated_at: datetime
    version: int

class Location(BaseModel):
    zip_code: str
    city: str
    state: str
    country: str = "USA"

class InsuranceInfo(BaseModel):
    provider: str
    policy_number: str  # encrypted
    group_number: Optional[str]
    plan_type: str
    coverage_details: Dict[str, Any]
```

### Procedure
```python
class Procedure(BaseModel):
    id: str
    name: str
    category: str
    description: str
    typical_cost_range: Tuple[int, int]
    recovery_days: int
    risk_level: str
    cpt_codes: List[str]
    icd10_codes: List[str]
    prompt_template: str  # For Gemini generation

class ProcedureCategory(str, Enum):
    FACIAL = "facial"
    BODY = "body"
    RECONSTRUCTIVE = "reconstructive"
    COSMETIC = "cosmetic"
```

### Visualization Result
```python
class VisualizationResult(BaseModel):
    id: str
    patient_id: str
    procedure_id: str
    before_image_url: str
    after_image_url: str
    prompt_used: str
    generated_at: datetime
    confidence_score: float
    embedding: List[float]
    metadata: Dict[str, Any]

class SimilarCase(BaseModel):
    id: str
    before_image_url: str
    after_image_url: str
    procedure_type: str
    similarity_score: float
    outcome_rating: float
    patient_satisfaction: int
    anonymized: bool = True
```

### Cost Breakdown
```python
class CostBreakdown(BaseModel):
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

class PaymentPlan(BaseModel):
    name: str
    monthly_payment: Decimal
    duration_months: int
    interest_rate: Decimal
    total_paid: Decimal
```

### Insurance Documentation
```python
class PreAuthForm(BaseModel):
    id: str
    patient_id: str
    procedure_id: str
    cpt_codes: List[str]
    icd10_codes: List[str]
    medical_justification: str
    cost_breakdown: CostBreakdown
    provider_info: ProviderInfo
    generated_at: datetime
    pdf_url: Optional[str]
    structured_data: Dict[str, Any]

class ProviderInfo(BaseModel):
    name: str
    npi: str
    address: str
    phone: str
    specialty: str
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Image validation consistency
*For any* uploaded image file, the validation function should accept files that meet format (JPEG/PNG/WebP), size (≤10MB), and quality requirements, and reject all others
**Validates: Requirements 1.1**

### Property 2: Procedure display completeness
*For any* surgical procedure, when displayed to a patient, the system should include description, typical recovery time, and risk factors in the output
**Validates: Requirements 1.2**

### Property 3: Profile field completeness
*For any* patient profile creation, the system should require and store name, date of birth, insurance provider, policy number, and location
**Validates: Requirements 2.1**

### Property 4: Insurance validation
*For any* insurance provider input, the validation function should return true for providers in the supported database and false for all others
**Validates: Requirements 2.2**

### Property 5: Sensitive data encryption
*For any* patient profile save operation, all sensitive fields (policy number, medical history) should be encrypted in storage such that raw values are not readable
**Validates: Requirements 2.3**

### Property 6: Version history preservation
*For any* profile update operation, the system should increment the version number and maintain a history record of the previous state
**Validates: Requirements 2.4**

### Property 7: Incomplete profile detection
*For any* patient profile with missing required fields, the validation function should identify and return all missing field names
**Validates: Requirements 2.5**

### Property 8: Cost breakdown completeness
*For any* cost estimate calculation, the breakdown should include surgeon fee, facility fee, anesthesia fee, and post-operative care as separate line items
**Validates: Requirements 3.1**

### Property 9: Geographic cost variation
*For any* procedure, calculating costs for two different geographic locations should produce different total costs (unless locations have identical pricing)
**Validates: Requirements 3.2**

### Property 10: Insurance calculation completeness
*For any* cost estimate with valid insurance information, the result should include calculated values for coverage, deductible, copay, and out-of-pocket maximum
**Validates: Requirements 3.3**

### Property 11: Dual format cost output
*For any* cost estimate generation, the system should produce both a text breakdown and an image file (PNG or JPEG) as output
**Validates: Requirements 3.4**

### Property 12: Payment plan inclusion
*For any* completed cost calculation, the result should include at least one payment plan option with monthly payment, duration, and interest rate
**Validates: Requirements 3.5**

### Property 13: Comparison source consistency
*For any* multi-procedure comparison, all generated visualizations should reference the same source image identifier
**Validates: Requirements 4.1**

### Property 14: Comparison data completeness
*For any* procedure comparison, the output should include cost differences, recovery time differences, and risk profile differences for all compared procedures
**Validates: Requirements 4.3**

### Property 15: Comparison persistence round-trip
*For any* saved comparison, retrieving it from storage should return a comparison set with the same procedures, visualizations, and metadata
**Validates: Requirements 4.4**

### Property 16: Embedding generation
*For any* uploaded image, the system should generate a vector embedding and store it in Qdrant with a valid embedding ID
**Validates: Requirements 5.1**

### Property 17: Similar case filtering
*For any* similar case search with specified filters (procedure type, age range), all returned results should match the filter criteria
**Validates: Requirements 5.2**

### Property 18: Search result completeness
*For any* similar case in search results, the result should include anonymized before/after images, outcome rating, and patient satisfaction score
**Validates: Requirements 5.3**

### Property 19: Similarity information display
*For any* similar case view, the display should include both a numerical similarity score and a text explanation of matching criteria
**Validates: Requirements 5.4**

### Property 20: Multi-filter application
*For any* similar case retrieval with multiple filters (procedure type, outcome quality, recency), all returned results should satisfy all specified filters
**Validates: Requirements 5.5**

### Property 21: Cost estimate transparency
*For any* cost estimate, the output should include citations of data sources and documentation of calculation methods used
**Validates: Requirements 6.4**

### Property 22: Medical disclaimer inclusion
*For any* medical information display (procedure details, cost estimates, visualizations), the output should include disclaimer text stating results are estimates requiring professional consultation
**Validates: Requirements 6.5**

### Property 23: Claim documentation completeness
*For any* insurance claim generation, the output should include procedure codes (CPT), medical necessity justification, and cost breakdown
**Validates: Requirements 7.1**

### Property 24: Dual format claim output
*For any* claim document generation, the system should produce both a PDF file and structured data (JSON) as output
**Validates: Requirements 7.2**

### Property 25: Claim information completeness
*For any* completed claim document, it should include patient information section, provider information section, and procedure details section
**Validates: Requirements 7.4**

### Property 26: Authentication enforcement
*For any* API request to protected endpoints, unauthenticated requests should be rejected with 401 status, and only authenticated requests should be processed
**Validates: Requirements 9.1**

### Property 27: AI service orchestration
*For any* surgical visualization request, the system should make calls to both Gemini 2.5 Flash Image API and record the interaction
**Validates: Requirements 9.2**

### Property 28: Freepik integration
*For any* enhanced visualization request, the system should call Freepik API for image generation or enhancement
**Validates: Requirements 9.3**

### Property 29: Qdrant vector operations
*For any* embedding storage or similarity search operation, the system should use Qdrant client for vector database interactions
**Validates: Requirements 9.4**

### Property 30: Export report completeness
*For any* export request, the generated report should include all patient visualizations, all cost estimates, and all saved comparisons
**Validates: Requirements 10.1**

### Property 31: Multi-format export support
*For any* export operation, the system should be capable of generating output in PDF, PNG, JPEG, and JSON formats
**Validates: Requirements 10.2**

### Property 32: Export metadata inclusion
*For any* generated export file, it should include a timestamp, patient name, and unique report identifier in the metadata or header
**Validates: Requirements 10.3**

### Property 33: Shareable export sanitization
*For any* export with "shareable" option selected, the output should not contain sensitive fields (policy number, medical history), while non-shareable exports should include all data
**Validates: Requirements 10.5**

## Error Handling

### Frontend Error Handling

**Network Errors:**
- Display user-friendly messages for connection failures
- Implement retry logic with exponential backoff
- Show offline mode indicator when backend is unreachable
- Cache recent data for offline viewing

**Validation Errors:**
- Real-time field validation with inline error messages
- Clear indication of which fields need correction
- Prevent form submission until all validations pass
- Preserve user input during validation failures

**AI Service Errors:**
- Graceful degradation when Gemini/Nano Banana unavailable
- Display estimated wait time for retries
- Offer alternative actions (save for later, try different procedure)
- Log errors for debugging without exposing technical details to users

### Backend Error Handling

**API Integration Errors:**
```python
class AIServiceError(Exception):
    """Base exception for AI service failures."""
    pass

class GeminiAPIError(AIServiceError):
    """Gemini API specific errors."""
    pass

class QdrantConnectionError(Exception):
    """Qdrant connection failures."""
    pass

# Error handling pattern
async def generate_visualization_with_retry(
    image: bytes,
    prompt: str,
    max_retries: int = 3
) -> VisualizationResult:
    for attempt in range(max_retries):
        try:
            result = await gemini_client.generate_image(image, prompt)
            return result
        except GeminiAPIError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    raise GeminiAPIError("Max retries exceeded")
```

**Data Validation Errors:**
- Use Pydantic for automatic validation
- Return 422 status with detailed field errors
- Sanitize all user inputs to prevent injection attacks
- Validate file uploads for malicious content

**Database Errors:**
- Implement connection pooling with health checks
- Automatic reconnection on connection loss
- Transaction rollback on failures
- Detailed logging for debugging

**Rate Limiting:**
- Implement per-user rate limits (100 requests/hour)
- Return 429 status with retry-after header
- Queue requests during high load
- Priority queue for paid users

### Security Error Handling

**Authentication Failures:**
- Clear error messages without revealing system details
- Account lockout after 5 failed attempts
- Require password reset after lockout
- Log all authentication failures for security monitoring

**Authorization Failures:**
- Return 403 status for insufficient permissions
- Log unauthorized access attempts
- Never reveal existence of resources user can't access
- Audit trail for all authorization decisions

**Data Encryption Errors:**
- Fail closed - reject operations if encryption fails
- Alert administrators on encryption failures
- Never store unencrypted sensitive data
- Regular encryption key rotation

## Testing Strategy

DocWiz will employ a comprehensive testing strategy combining unit tests, property-based tests, and integration tests to ensure correctness, security, and reliability.

### Property-Based Testing

**Framework:** We will use **Hypothesis** for Python backend testing and **fast-check** for TypeScript frontend testing.

**Configuration:**
- Minimum 100 iterations per property test
- Shrinking enabled to find minimal failing examples
- Deterministic seed for reproducible test runs
- Custom generators for domain-specific data types

**Property Test Implementation:**

Each correctness property from the design document will be implemented as a property-based test with explicit tagging:

```python
from hypothesis import given, strategies as st
import pytest

@given(
    image_data=st.binary(min_size=1024, max_size=10*1024*1024),
    format=st.sampled_from(['jpeg', 'png', 'webp', 'gif', 'bmp'])
)
@pytest.mark.property_test
def test_image_validation_consistency(image_data, format):
    """
    Feature: docwiz-surgical-platform, Property 1: Image validation consistency
    
    For any uploaded image file, the validation function should accept files
    that meet format (JPEG/PNG/WebP), size (≤10MB), and quality requirements,
    and reject all others.
    """
    result = validate_image(image_data, format)
    
    valid_formats = ['jpeg', 'png', 'webp']
    size_valid = len(image_data) <= 10 * 1024 * 1024
    
    if format in valid_formats and size_valid:
        assert result.is_valid
    else:
        assert not result.is_valid
```

**Custom Generators:**

```python
# Custom strategies for domain models
@st.composite
def patient_profile_strategy(draw):
    return PatientProfile(
        name=draw(st.text(min_size=1, max_size=100)),
        date_of_birth=draw(st.dates(min_value=date(1920, 1, 1))),
        insurance_provider=draw(st.sampled_from(VALID_PROVIDERS)),
        policy_number=draw(st.text(min_size=5, max_size=20)),
        location=draw(location_strategy())
    )

@st.composite
def procedure_strategy(draw):
    return Procedure(
        id=draw(st.uuids()),
        name=draw(st.text(min_size=5, max_size=50)),
        category=draw(st.sampled_from(ProcedureCategory)),
        typical_cost_range=(
            draw(st.integers(min_value=1000, max_value=50000)),
            draw(st.integers(min_value=50000, max_value=200000))
        )
    )
```

**Property Test Requirements:**
- Each property test MUST run at least 100 iterations
- Each property test MUST be tagged with: `Feature: docwiz-surgical-platform, Property {number}: {property_text}`
- Each property test MUST reference the requirements it validates
- Property tests SHOULD use realistic data generators
- Property tests SHOULD NOT use mocks for core business logic

### Unit Testing

**Framework:** pytest for Python, Jest for TypeScript

**Unit Test Coverage:**

```python
# Example unit tests for specific scenarios
def test_cost_calculation_with_insurance():
    """Test specific example of cost calculation with insurance."""
    procedure = create_test_procedure(cost=10000)
    insurance = create_test_insurance(coverage=0.8, deductible=1000)
    
    breakdown = calculate_cost_breakdown(procedure, insurance)
    
    assert breakdown.total_cost == 10000
    assert breakdown.insurance_coverage == 8000
    assert breakdown.patient_responsibility == 3000  # 1000 deductible + 2000 copay

def test_empty_profile_validation():
    """Test that empty profile is rejected."""
    profile = PatientProfile()
    
    errors = validate_profile(profile)
    
    assert 'name' in errors
    assert 'date_of_birth' in errors
    assert 'insurance_provider' in errors
```

**Unit Test Focus:**
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary values, null handling)
- Error conditions and exception handling
- Integration points between components
- Mock external API calls (Gemini, Freepik, Qdrant)

### Integration Testing

**Scope:**
- End-to-end API workflows
- Database operations with real PostgreSQL
- Qdrant vector operations
- File upload and storage
- Authentication and authorization flows

**Example Integration Test:**

```python
@pytest.mark.integration
async def test_full_visualization_workflow(test_client, test_db):
    """Test complete visualization generation workflow."""
    # Create patient profile
    profile_response = await test_client.post('/api/profiles', json={
        'name': 'Test Patient',
        'date_of_birth': '1990-01-01',
        'insurance_provider': 'Blue Cross',
        'policy_number': 'BC123456',
        'location': {'zip_code': '94102'}
    })
    assert profile_response.status_code == 201
    
    # Upload image
    with open('test_image.jpg', 'rb') as f:
        upload_response = await test_client.post(
            '/api/images/upload',
            files={'image': f}
        )
    assert upload_response.status_code == 200
    image_id = upload_response.json()['id']
    
    # Generate visualization
    viz_response = await test_client.post('/api/visualizations', json={
        'image_id': image_id,
        'procedure_id': 'rhinoplasty-001',
        'patient_id': profile_response.json()['id']
    })
    assert viz_response.status_code == 200
    assert 'after_image_url' in viz_response.json()
```

### Test Data Management

**Fixtures:**
- Reusable test data factories
- Database fixtures with rollback
- Mock API responses for external services
- Sample images for upload testing

**Test Database:**
- Separate test database instance
- Automatic schema migration before tests
- Transaction rollback after each test
- Seed data for consistent testing

### Performance Testing

**Load Testing:**
- Simulate 100 concurrent users
- Test API response times under load
- Verify 95th percentile < 2 seconds
- Monitor memory and CPU usage

**Tools:**
- Locust for load testing
- pytest-benchmark for performance regression
- Memory profiler for leak detection

### Security Testing

**Security Test Coverage:**
- SQL injection prevention
- XSS prevention in user inputs
- CSRF token validation
- Authentication bypass attempts
- Authorization boundary testing
- Encryption verification
- HIPAA compliance validation

### Continuous Integration

**CI Pipeline:**
1. Lint and format check (black, flake8, eslint)
2. Type checking (mypy, TypeScript)
3. Unit tests (fast feedback)
4. Property-based tests (100+ iterations)
5. Integration tests (with test database)
6. Security scanning (bandit, npm audit)
7. Coverage report (minimum 80%)

**Test Execution:**
- Run on every pull request
- Block merge if tests fail
- Generate coverage reports
- Alert on coverage decrease

## Design Decisions and Rationales

### 1. Next.js for Frontend

**Decision:** Use Next.js with App Router instead of plain React

**Rationale:**
- Server-side rendering improves initial load time (Requirement 8.1)
- Built-in API routes for backend-for-frontend pattern
- Automatic code splitting reduces bundle size
- Image optimization for surgical previews
- SEO benefits for marketing pages

### 2. FastAPI for Backend

**Decision:** Use FastAPI instead of Flask or Django

**Rationale:**
- Native async/await support for concurrent AI API calls
- Automatic OpenAPI documentation
- Pydantic integration for data validation
- High performance (comparable to Node.js)
- Type hints improve code quality

### 3. Qdrant for Vector Search

**Decision:** Use Qdrant instead of Pinecone or Weaviate

**Rationale:**
- Open-source with self-hosting option
- Excellent performance for similarity search
- Rich filtering capabilities (procedure type, age, etc.)
- Python and TypeScript client libraries
- Cost-effective for hackathon and MVP

### 4. PostgreSQL for Relational Data

**Decision:** Use PostgreSQL instead of MongoDB

**Rationale:**
- ACID compliance for financial data (cost estimates)
- Strong data integrity for patient profiles
- JSON support for flexible metadata
- Mature ecosystem and tooling
- Better for complex queries (cost calculations)

### 5. Separate Storage for Images

**Decision:** Use object storage (S3/R2) instead of database BLOBs

**Rationale:**
- Better performance for large files
- CDN integration for fast delivery
- Cost-effective storage
- Easier backup and replication
- Scalability for growing image library

### 6. Zustand for State Management

**Decision:** Use Zustand instead of Redux or Context API

**Rationale:**
- Minimal boilerplate (surgically effective!)
- TypeScript-first design
- No provider wrapper needed
- Excellent performance
- Easy to test

### 7. Tailwind CSS for Styling

**Decision:** Use Tailwind instead of styled-components or CSS modules

**Rationale:**
- Rapid development with utility classes
- Consistent design system
- Small production bundle (purged unused styles)
- Responsive design utilities
- Easy to maintain "surgically effective" aesthetic

### 8. Hypothesis for Property Testing

**Decision:** Use Hypothesis instead of writing custom generators

**Rationale:**
- Mature property-based testing library
- Excellent shrinking for minimal failing examples
- Rich strategy library
- Good documentation
- Active community

### 9. JWT for Authentication

**Decision:** Use JWT tokens instead of session-based auth

**Rationale:**
- Stateless authentication (scales better)
- Works well with mobile apps (future)
- Can include user claims (role, permissions)
- Standard format (RFC 7519)
- Easy to implement with FastAPI

### 10. Celery for Async Tasks

**Decision:** Use Celery for background jobs instead of inline processing

**Rationale:**
- Long-running AI API calls don't block requests
- Retry logic for failed API calls
- Task scheduling for batch operations
- Monitoring and debugging tools
- Scales horizontally

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/docwiz
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - qdrant
      - redis
  
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - postgres
```

### Production Considerations

**Infrastructure:**
- Frontend: Vercel or Netlify (automatic deployments)
- Backend: AWS ECS or Google Cloud Run (containerized)
- Database: AWS RDS PostgreSQL (managed)
- Vector DB: Self-hosted Qdrant on EC2/GCE
- Object Storage: AWS S3 or Cloudflare R2
- CDN: CloudFront or Cloudflare

**Monitoring:**
- Application: Sentry for error tracking
- Performance: New Relic or DataDog
- Logs: CloudWatch or Elasticsearch
- Uptime: Pingdom or UptimeRobot

**Security:**
- SSL/TLS certificates (Let's Encrypt)
- WAF for DDoS protection
- Rate limiting (Redis-based)
- Data encryption at rest and in transit
- Regular security audits
- HIPAA compliance measures

**Scalability:**
- Horizontal scaling for backend (load balancer)
- Database read replicas
- Redis cluster for caching
- CDN for static assets
- Auto-scaling based on load

## API Design

### RESTful Endpoints

**Authentication:**
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
```

**Patient Profiles:**
```
POST   /api/profiles
GET    /api/profiles/:id
PUT    /api/profiles/:id
GET    /api/profiles/:id/history
```

**Image Upload:**
```
POST   /api/images/upload
GET    /api/images/:id
DELETE /api/images/:id
```

**Procedures:**
```
GET    /api/procedures
GET    /api/procedures/:id
GET    /api/procedures/categories
```

**Visualizations:**
```
POST   /api/visualizations
GET    /api/visualizations/:id
POST   /api/visualizations/compare
GET    /api/visualizations/:id/similar
```

**Cost Estimates:**
```
POST   /api/costs/estimate
GET    /api/costs/:id
GET    /api/costs/:id/infographic
POST   /api/costs/:id/payment-plans
```

**Insurance:**
```
POST   /api/insurance/validate
POST   /api/insurance/claims
GET    /api/insurance/claims/:id/pdf
```

**Exports:**
```
POST   /api/exports
GET    /api/exports/:id
GET    /api/exports/:id/download
```

### WebSocket Endpoints

**Real-time Updates:**
```
WS     /ws/visualizations/:id
WS     /ws/costs/:id
```

Used for streaming progress updates during long-running AI operations.

## UI/UX Design Principles

### Surgically Effective Design

**Visual Hierarchy:**
- Clean, minimal layouts with ample whitespace
- Surgical blue (#0066CC) as primary accent color
- Neutral grays for backgrounds (#F5F5F5, #E0E0E0)
- High contrast for readability (WCAG AAA)
- Professional medical aesthetic

**Typography:**
- Primary: Inter (clean, modern, readable)
- Monospace: JetBrains Mono (for data/numbers)
- Font sizes: 14px body, 16px important, 24px+ headings
- Line height: 1.5 for body text

**Components:**
- Rounded corners (4px) for subtle softness
- Subtle shadows for depth (surgical precision)
- Smooth transitions (200ms ease-in-out)
- Loading states with skeleton screens
- Toast notifications for feedback

**Layout:**
- Responsive grid system (12 columns)
- Mobile-first approach
- Sticky navigation for easy access
- Breadcrumbs for complex workflows
- Progress indicators for multi-step processes

### User Flows

**Primary Flow: Surgical Visualization**
1. Upload photo (drag-and-drop or file picker)
2. Select procedure (searchable list with categories)
3. Review procedure details (modal with info)
4. Generate preview (loading state with progress)
5. View before/after (slider comparison)
6. Save or regenerate (action buttons)

**Secondary Flow: Cost Estimation**
1. Complete profile (if not done)
2. Select procedure (from visualization or separately)
3. Review cost breakdown (interactive chart)
4. Explore payment plans (expandable cards)
5. Export or save (multiple format options)

**Tertiary Flow: Similar Cases**
1. Upload photo (reuse from visualization)
2. View similar cases (grid layout)
3. Filter results (sidebar filters)
4. Compare outcomes (side-by-side view)
5. Save favorites (bookmark icon)

## Future Enhancements

**Phase 2 Features:**
- Video previews showing healing progression
- 3D facial modeling for more accurate previews
- Surgeon marketplace integration
- Appointment booking system
- Patient community forum
- Mobile apps (iOS/Android)

**AI Improvements:**
- Fine-tuned models for specific procedures
- Multi-angle photo support
- Age progression/regression
- Skin tone and texture matching
- Scar prediction and visualization

**Business Features:**
- Surgeon dashboard for patient management
- Insurance provider integrations
- Payment processing
- Telemedicine consultations
- Medical records integration (FHIR)

**Analytics:**
- Patient decision tracking
- Procedure popularity trends
- Cost comparison analytics
- Outcome satisfaction metrics
- A/B testing for UI improvements
