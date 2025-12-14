# DocWiz API Documentation

## Overview

The DocWiz API is a RESTful API built with FastAPI that provides surgical visualization, cost estimation, and insurance documentation services. All endpoints require authentication unless otherwise specified.

**Base URL:** `http://localhost:8000/api`

**API Version:** 1.0

## Authentication

DocWiz uses JWT (JSON Web Token) bearer authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Authentication Flow

1. Register a new user or login with existing credentials
2. Receive JWT access token
3. Include token in all subsequent requests
4. Refresh token before expiration

### Token Expiration

- Access tokens expire after 60 minutes (configurable)
- Use the `/auth/refresh` endpoint to get a new token
- Expired tokens return 401 Unauthorized

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limiting

- 100 requests per hour per user
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets


---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `201 Created`
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `400` - Email already registered

---

### POST /auth/login

Login and receive JWT access token.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` - Incorrect email or password

---

### POST /auth/refresh

Refresh JWT access token.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### POST /auth/logout

Logout user (client should discard token).

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

### GET /auth/me

Get current user information.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```


---

## Profile Endpoints

### GET /profiles/me

Get current user's patient profile.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": "profile_123",
  "user_id": "user_123",
  "name": "John Doe",
  "date_of_birth": "1990-01-15",
  "location": {
    "zip_code": "94102",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  },
  "insurance_info": {
    "provider": "Blue Cross Blue Shield",
    "policy_number": "BC123456789",
    "plan_type": "PPO"
  },
  "medical_history": "No significant medical history",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "version": 1
}
```

**Errors:**
- `404` - Profile not found

---

### POST /profiles

Create a new patient profile.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "John Doe",
  "date_of_birth": "1990-01-15",
  "location": {
    "zip_code": "94102",
    "city": "San Francisco",
    "state": "CA"
  },
  "insurance_info": {
    "provider": "Blue Cross Blue Shield",
    "policy_number": "BC123456789",
    "plan_type": "PPO"
  },
  "medical_history": "No significant medical history"
}
```

**Response:** `201 Created`
```json
{
  "id": "profile_123",
  "user_id": "user_123",
  "name": "John Doe",
  "date_of_birth": "1990-01-15",
  "location": {
    "zip_code": "94102",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  },
  "insurance_info": {
    "provider": "Blue Cross Blue Shield",
    "policy_number": "BC123456789",
    "plan_type": "PPO"
  },
  "medical_history": "No significant medical history",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "version": 1
}
```

**Errors:**
- `422` - Validation failed (missing or invalid fields)


---

### GET /profiles/{profile_id}

Get patient profile by ID.

**Authentication:** Required

**Path Parameters:**
- `profile_id` (string) - Profile identifier

**Response:** `200 OK`
```json
{
  "id": "profile_123",
  "user_id": "user_123",
  "name": "John Doe",
  "date_of_birth": "1990-01-15",
  "location": {
    "zip_code": "94102",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  },
  "insurance_info": {
    "provider": "Blue Cross Blue Shield",
    "policy_number": "BC123456789",
    "plan_type": "PPO"
  },
  "medical_history": "No significant medical history",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "version": 1
}
```

**Errors:**
- `403` - Not authorized to access this profile
- `404` - Profile not found

---

### PUT /profiles/{profile_id}

Update patient profile.

**Authentication:** Required

**Path Parameters:**
- `profile_id` (string) - Profile identifier

**Request Body:**
```json
{
  "name": "John Doe",
  "location": {
    "zip_code": "94103"
  },
  "insurance_info": {
    "plan_type": "HMO"
  }
}
```

**Response:** `200 OK`
```json
{
  "id": "profile_123",
  "user_id": "user_123",
  "name": "John Doe",
  "date_of_birth": "1990-01-15",
  "location": {
    "zip_code": "94103",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA"
  },
  "insurance_info": {
    "provider": "Blue Cross Blue Shield",
    "policy_number": "BC123456789",
    "plan_type": "HMO"
  },
  "medical_history": "No significant medical history",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "version": 2
}
```

**Errors:**
- `403` - Not authorized to update this profile
- `404` - Profile not found

---

### GET /profiles/{profile_id}/history

Get profile version history.

**Authentication:** Required

**Path Parameters:**
- `profile_id` (string) - Profile identifier

**Response:** `200 OK`
```json
[
  {
    "version": 1,
    "updated_at": "2024-01-15T10:30:00Z",
    "changes": {
      "created": true
    }
  },
  {
    "version": 2,
    "updated_at": "2024-01-15T11:00:00Z",
    "changes": {
      "location.zip_code": "94103",
      "insurance_info.plan_type": "HMO"
    }
  }
]
```

**Errors:**
- `403` - Not authorized to access this profile history
- `404` - Profile not found


---

## Image Endpoints

### POST /images/upload

Upload a patient image for surgical visualization.

**Authentication:** Required

**Request:** Multipart form data
- `file` (file) - Image file (JPEG, PNG, or WebP, max 10MB)

**Response:** `200 OK`
```json
{
  "id": "img_123",
  "url": "https://storage.example.com/images/img_123.jpg",
  "width": 1920,
  "height": 1080,
  "format": "JPEG",
  "size_bytes": 524288,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `400` - Image validation failed (invalid format, size, or quality)

---

### GET /images/{image_id}

Get image metadata by ID.

**Authentication:** Required

**Path Parameters:**
- `image_id` (string) - Image identifier

**Response:** `200 OK`
```json
{
  "id": "img_123",
  "user_id": "user_123",
  "url": "https://storage.example.com/images/img_123.jpg",
  "width": 1920,
  "height": 1080,
  "format": "JPEG",
  "size_bytes": 524288,
  "original_filename": "photo.jpg",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- `403` - Access denied to this image
- `404` - Image not found

---

### DELETE /images/{image_id}

Delete image by ID.

**Authentication:** Required

**Path Parameters:**
- `image_id` (string) - Image identifier

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Image img_123 deleted successfully"
}
```

**Errors:**
- `403` - Access denied to this image
- `404` - Image not found


---

## Procedure Endpoints

### GET /procedures

List all available surgical procedures.

**Authentication:** Not required

**Query Parameters:**
- `category` (string, optional) - Filter by category (e.g., 'facial', 'body', 'reconstructive')
- `search` (string, optional) - Search by name or description

**Response:** `200 OK`
```json
{
  "procedures": [
    {
      "id": "proc_rhinoplasty",
      "name": "Rhinoplasty",
      "category": "facial",
      "description": "Surgical reshaping of the nose",
      "typical_cost_min": 5000,
      "typical_cost_max": 15000,
      "recovery_days": 14,
      "risk_level": "medium",
      "cpt_codes": ["30400", "30410"],
      "icd10_codes": ["J34.2"]
    }
  ],
  "total": 1
}
```

---

### GET /procedures/categories

List all procedure categories.

**Authentication:** Not required

**Response:** `200 OK`
```json
{
  "categories": ["facial", "body", "reconstructive", "cosmetic"],
  "total": 4
}
```

---

### GET /procedures/{procedure_id}

Get procedure details by ID.

**Authentication:** Not required

**Path Parameters:**
- `procedure_id` (string) - Procedure identifier

**Response:** `200 OK`
```json
{
  "id": "proc_rhinoplasty",
  "name": "Rhinoplasty",
  "category": "facial",
  "description": "Surgical reshaping of the nose to improve appearance or function",
  "recovery_days": 14,
  "risk_level": "medium",
  "cost_range": {
    "min": 5000,
    "max": 15000
  }
}
```

**Errors:**
- `404` - Procedure not found

---

### POST /procedures/initialize

Initialize procedures in database from seed data.

**Authentication:** Required (Admin only)

**Response:** `200 OK`
```json
{
  "message": "Successfully initialized 25 procedures",
  "count": 25
}
```


---

## Visualization Endpoints

### POST /visualizations

Generate a surgical visualization.

**Authentication:** Required

**Query Parameters:**
- `async_processing` (boolean, default: false) - Process asynchronously using Celery

**Request Body:**
```json
{
  "image_id": "img_123",
  "procedure_id": "proc_rhinoplasty",
  "patient_id": "profile_123"
}
```

**Response (Synchronous):** `200 OK`
```json
{
  "id": "viz_123",
  "patient_id": "profile_123",
  "procedure_id": "proc_rhinoplasty",
  "before_image_url": "https://storage.example.com/images/img_123.jpg",
  "after_image_url": "https://storage.example.com/visualizations/viz_123_after.jpg",
  "prompt_used": "Generate realistic rhinoplasty result...",
  "generated_at": "2024-01-15T10:35:00Z",
  "confidence_score": 0.92,
  "metadata": {
    "model": "gemini-2.5-flash-image",
    "processing_time_ms": 8500
  }
}
```

**Response (Asynchronous):** `200 OK`
```json
{
  "task_id": "task_abc123",
  "status": "processing",
  "message": "Visualization generation started. Use task_id to track progress.",
  "status_url": "/api/tasks/task_abc123/status",
  "websocket_url": "/api/ws/tasks/task_abc123"
}
```

**Errors:**
- `400` - Invalid request (image or procedure not found)
- `500` - Generation failed

---

### GET /visualizations/{visualization_id}

Get visualization by ID.

**Authentication:** Required

**Path Parameters:**
- `visualization_id` (string) - Visualization identifier

**Response:** `200 OK`
```json
{
  "id": "viz_123",
  "patient_id": "profile_123",
  "procedure_id": "proc_rhinoplasty",
  "before_image_url": "https://storage.example.com/images/img_123.jpg",
  "after_image_url": "https://storage.example.com/visualizations/viz_123_after.jpg",
  "prompt_used": "Generate realistic rhinoplasty result...",
  "generated_at": "2024-01-15T10:35:00Z",
  "confidence_score": 0.92,
  "metadata": {
    "model": "gemini-2.5-flash-image",
    "processing_time_ms": 8500
  }
}
```

**Errors:**
- `404` - Visualization not found


---

### GET /visualizations/{visualization_id}/similar

Find similar surgical cases.

**Authentication:** Required

**Path Parameters:**
- `visualization_id` (string) - Visualization identifier

**Query Parameters:**
- `procedure_type` (string, optional) - Filter by procedure type
- `age_range` (string, optional) - Filter by age range (e.g., '20-30')
- `min_outcome_rating` (float, optional) - Minimum outcome rating (0.0-1.0)
- `limit` (integer, default: 10, max: 50) - Maximum number of results

**Response:** `200 OK`
```json
{
  "query_visualization_id": "viz_123",
  "similar_cases": [
    {
      "id": "case_456",
      "before_image_url": "https://storage.example.com/cases/case_456_before.jpg",
      "after_image_url": "https://storage.example.com/cases/case_456_after.jpg",
      "procedure_type": "rhinoplasty",
      "similarity_score": 0.89,
      "outcome_rating": 0.95,
      "patient_satisfaction": 5,
      "age_range": "25-30",
      "anonymized": true,
      "matching_criteria": "Similar facial structure and procedure type"
    }
  ],
  "total_found": 1,
  "filters_applied": {
    "procedure_type": "rhinoplasty",
    "min_outcome_rating": 0.8
  }
}
```

**Errors:**
- `400` - Invalid filters
- `404` - Visualization not found

---

### POST /visualizations/compare

Compare multiple procedures side-by-side.

**Authentication:** Required

**Query Parameters:**
- `async_processing` (boolean, default: false) - Process asynchronously using Celery

**Request Body:**
```json
{
  "source_image_id": "img_123",
  "procedure_ids": ["proc_rhinoplasty", "proc_septoplasty"],
  "patient_id": "profile_123"
}
```

**Response (Synchronous):** `200 OK`
```json
{
  "id": "comp_789",
  "patient_id": "profile_123",
  "source_image_id": "img_123",
  "visualizations": [
    {
      "procedure_id": "proc_rhinoplasty",
      "procedure_name": "Rhinoplasty",
      "after_image_url": "https://storage.example.com/comparisons/comp_789_rhino.jpg"
    },
    {
      "procedure_id": "proc_septoplasty",
      "procedure_name": "Septoplasty",
      "after_image_url": "https://storage.example.com/comparisons/comp_789_septo.jpg"
    }
  ],
  "cost_comparison": [
    {
      "procedure_id": "proc_rhinoplasty",
      "total_cost": 12000,
      "patient_responsibility": 3000
    },
    {
      "procedure_id": "proc_septoplasty",
      "total_cost": 8000,
      "patient_responsibility": 2000
    }
  ],
  "recovery_comparison": [14, 10],
  "risk_comparison": ["medium", "low"],
  "created_at": "2024-01-15T10:40:00Z"
}
```

**Response (Asynchronous):** `200 OK`
```json
{
  "task_id": "task_def456",
  "status": "processing",
  "message": "Comparison generation started. Use task_id to track progress.",
  "status_url": "/api/tasks/task_def456/status",
  "websocket_url": "/api/ws/tasks/task_def456"
}
```

**Errors:**
- `400` - Invalid request (must specify 2+ procedures)

---

### GET /visualizations/comparisons/{comparison_id}

Get comparison by ID.

**Authentication:** Required

**Path Parameters:**
- `comparison_id` (string) - Comparison identifier

**Response:** `200 OK`
```json
{
  "comparison": {
    "id": "comp_789",
    "patient_id": "profile_123",
    "source_image_id": "img_123",
    "visualizations": [...],
    "cost_comparison": [...],
    "recovery_comparison": [14, 10],
    "risk_comparison": ["medium", "low"],
    "created_at": "2024-01-15T10:40:00Z"
  }
}
```

**Errors:**
- `404` - Comparison not found


---

## Cost Estimation Endpoints

### POST /costs/estimate

Calculate cost estimate for a procedure.

**Authentication:** Required

**Request Body:**
```json
{
  "procedure_id": "proc_rhinoplasty",
  "patient_id": "profile_123"
}
```

**Response:** `201 Created`
```json
{
  "id": "cost_123",
  "procedure_id": "proc_rhinoplasty",
  "patient_id": "profile_123",
  "surgeon_fee": 6000.00,
  "facility_fee": 3000.00,
  "anesthesia_fee": 1500.00,
  "post_op_care": 1500.00,
  "total_cost": 12000.00,
  "insurance_coverage": 9000.00,
  "patient_responsibility": 3000.00,
  "deductible": 1000.00,
  "copay": 500.00,
  "out_of_pocket_max": 5000.00,
  "payment_plans": [
    {
      "name": "12-Month Plan",
      "monthly_payment": 260.00,
      "duration_months": 12,
      "interest_rate": 0.04,
      "total_paid": 3120.00
    }
  ],
  "calculated_at": "2024-01-15T10:45:00Z",
  "data_sources": [
    "FAIR Health Database",
    "Regional Cost Index"
  ]
}
```

**Errors:**
- `403` - Not authorized to access this profile
- `404` - Patient profile or procedure not found

---

### GET /costs/{cost_id}

Get cost breakdown by ID.

**Authentication:** Required

**Path Parameters:**
- `cost_id` (string) - Cost breakdown identifier

**Response:** `200 OK`
```json
{
  "id": "cost_123",
  "procedure_id": "proc_rhinoplasty",
  "patient_id": "profile_123",
  "surgeon_fee": 6000.00,
  "facility_fee": 3000.00,
  "anesthesia_fee": 1500.00,
  "post_op_care": 1500.00,
  "total_cost": 12000.00,
  "insurance_coverage": 9000.00,
  "patient_responsibility": 3000.00,
  "deductible": 1000.00,
  "copay": 500.00,
  "out_of_pocket_max": 5000.00,
  "payment_plans": [
    {
      "name": "12-Month Plan",
      "monthly_payment": 260.00,
      "duration_months": 12,
      "interest_rate": 0.04,
      "total_paid": 3120.00
    }
  ],
  "calculated_at": "2024-01-15T10:45:00Z",
  "data_sources": [
    "FAIR Health Database",
    "Regional Cost Index"
  ]
}
```

**Errors:**
- `403` - Not authorized to access this cost breakdown
- `404` - Cost breakdown not found

---

### GET /costs/{cost_id}/infographic

Get visual cost breakdown infographic.

**Authentication:** Required

**Path Parameters:**
- `cost_id` (string) - Cost breakdown identifier

**Query Parameters:**
- `format` (string, default: 'png') - Output format ('png' or 'jpeg')

**Response:** `200 OK`
```json
{
  "cost_id": "cost_123",
  "infographic_url": "https://storage.example.com/infographics/cost_123.png",
  "format": "png",
  "width": 1200,
  "height": 800
}
```

**Errors:**
- `400` - Invalid format
- `403` - Not authorized to access this cost breakdown
- `404` - Cost breakdown not found
- `500` - Failed to generate infographic


---

## Insurance Endpoints

### POST /insurance/validate

Validate insurance information.

**Authentication:** Required

**Request Body:**
```json
{
  "provider": "Blue Cross Blue Shield",
  "policy_number": "BC123456789"
}
```

**Response:** `200 OK`
```json
{
  "is_valid": true,
  "provider": "Blue Cross Blue Shield",
  "message": "Insurance provider Blue Cross Blue Shield is supported",
  "supported_procedures": null
}
```

---

### POST /insurance/claims

Generate insurance claim documentation.

**Authentication:** Required

**Request Body:**
```json
{
  "procedure_id": "proc_rhinoplasty",
  "patient_id": "profile_123",
  "cost_breakdown_id": "cost_123",
  "provider_info": {
    "name": "Dr. Jane Smith",
    "npi": "1234567890",
    "address": "123 Medical Plaza, San Francisco, CA 94102",
    "phone": "+1-415-555-0100",
    "specialty": "Plastic Surgery"
  }
}
```

**Response:** `200 OK`
```json
{
  "id": "claim_123",
  "patient_id": "profile_123",
  "procedure_id": "proc_rhinoplasty",
  "cost_breakdown_id": "cost_123",
  "cpt_codes": ["30400", "30410"],
  "icd10_codes": ["J34.2"],
  "medical_justification": "Patient presents with deviated septum causing breathing difficulties...",
  "provider_info": {
    "name": "Dr. Jane Smith",
    "npi": "1234567890",
    "address": "123 Medical Plaza, San Francisco, CA 94102",
    "phone": "+1-415-555-0100",
    "specialty": "Plastic Surgery"
  },
  "pdf_url": "https://storage.example.com/claims/claim_123.pdf",
  "structured_data": {
    "patient": {...},
    "procedure": {...},
    "costs": {...}
  },
  "generated_at": "2024-01-15T10:50:00Z"
}
```

**Errors:**
- `404` - Patient profile, procedure, or cost breakdown not found
- `500` - Failed to generate claim

---

### GET /insurance/claims/{claim_id}/pdf

Download claim as PDF.

**Authentication:** Required

**Path Parameters:**
- `claim_id` (string) - Claim identifier

**Response:** `200 OK`
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=preauth_form_{claim_id}.pdf`

**Errors:**
- `404` - Claim not found
- `500` - Failed to generate PDF

---

### GET /insurance/claims/{claim_id}/json

Download claim as JSON.

**Authentication:** Required

**Path Parameters:**
- `claim_id` (string) - Claim identifier

**Response:** `200 OK`
- Content-Type: `application/json`
- Content-Disposition: `attachment; filename=preauth_form_{claim_id}.json`

**Errors:**
- `404` - Claim not found
- `500` - Failed to generate JSON


---

## Export Endpoints

### POST /exports

Create a comprehensive export report.

**Authentication:** Required

**Query Parameters:**
- `async_processing` (boolean, default: false) - Process asynchronously using Celery

**Request Body:**
```json
{
  "patient_id": "profile_123",
  "format": "pdf",
  "shareable": false,
  "include_visualizations": true,
  "include_cost_estimates": true,
  "include_comparisons": true,
  "visualization_ids": ["viz_123"],
  "cost_breakdown_ids": ["cost_123"],
  "comparison_ids": ["comp_789"]
}
```

**Response (Synchronous):** `200 OK`
```json
{
  "id": "export_123",
  "patient_id": "profile_123",
  "patient_name": "John Doe",
  "format": "pdf",
  "shareable": false,
  "created_at": "2024-01-15T11:00:00Z",
  "status": "completed",
  "download_url": "/api/exports/export_123/download"
}
```

**Response (Asynchronous):** `200 OK`
```json
{
  "task_id": "task_ghi789",
  "status": "processing",
  "message": "Export generation started. Use task_id to track progress.",
  "status_url": "/api/tasks/task_ghi789/status",
  "websocket_url": "/api/ws/tasks/task_ghi789"
}
```

**Errors:**
- `400` - Invalid request
- `500` - Failed to create export

---

### GET /exports/{export_id}

Get export metadata.

**Authentication:** Required

**Path Parameters:**
- `export_id` (string) - Export identifier

**Response:** `200 OK`
```json
{
  "id": "export_123",
  "patient_id": "profile_123",
  "patient_name": "John Doe",
  "format": "pdf",
  "shareable": false,
  "file_size_bytes": 2048576,
  "created_at": "2024-01-15T11:00:00Z",
  "report_identifier": "DOCWIZ-2024-01-15-123"
}
```

**Errors:**
- `404` - Export not found
- `500` - Failed to retrieve export metadata

---

### GET /exports/{export_id}/download

Download export file.

**Authentication:** Required

**Path Parameters:**
- `export_id` (string) - Export identifier

**Response:** `200 OK`
- Content-Type: Varies by format
  - PDF: `application/pdf`
  - PNG: `image/png`
  - JPEG: `image/jpeg`
  - JSON: `application/json`
- Content-Disposition: `attachment; filename=docwiz_report_{export_id}.{ext}`

**Errors:**
- `404` - Export not found
- `500` - Failed to download export


---

## Task Management Endpoints

### GET /tasks/{task_id}/status

Get status of an asynchronous task.

**Authentication:** Required

**Path Parameters:**
- `task_id` (string) - Task identifier

**Response:** `200 OK`
```json
{
  "task_id": "task_abc123",
  "status": "processing",
  "progress": 45,
  "message": "Generating visualization...",
  "result": null,
  "error": null
}
```

**Task Statuses:**
- `pending` - Task queued but not started
- `processing` - Task in progress
- `completed` - Task completed successfully
- `failed` - Task failed with error

---

### WebSocket /ws/tasks/{task_id}

Real-time task progress updates via WebSocket.

**Authentication:** Required (via query parameter `token`)

**Connection URL:**
```
ws://localhost:8000/api/ws/tasks/{task_id}?token={jwt_token}
```

**Message Format:**
```json
{
  "task_id": "task_abc123",
  "status": "processing",
  "progress": 45,
  "message": "Generating visualization...",
  "timestamp": "2024-01-15T10:35:30Z"
}
```

---

## Data Models

### PatientProfile
```typescript
{
  id: string;
  user_id: string;
  name: string;
  date_of_birth: string; // ISO 8601 date
  location: {
    zip_code: string;
    city: string;
    state: string;
    country: string;
  };
  insurance_info: {
    provider: string;
    policy_number: string; // Encrypted
    plan_type: string;
  };
  medical_history?: string; // Encrypted
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  version: number;
}
```

### Procedure
```typescript
{
  id: string;
  name: string;
  category: string;
  description: string;
  typical_cost_min: number;
  typical_cost_max: number;
  recovery_days: number;
  risk_level: "low" | "medium" | "high";
  cpt_codes: string[];
  icd10_codes: string[];
}
```

### VisualizationResult
```typescript
{
  id: string;
  patient_id: string;
  procedure_id: string;
  before_image_url: string;
  after_image_url: string;
  prompt_used: string;
  generated_at: string; // ISO 8601 datetime
  confidence_score: number; // 0.0 - 1.0
  metadata: {
    model: string;
    processing_time_ms: number;
  };
}
```

### CostBreakdown
```typescript
{
  id: string;
  procedure_id: string;
  patient_id: string;
  surgeon_fee: number;
  facility_fee: number;
  anesthesia_fee: number;
  post_op_care: number;
  total_cost: number;
  insurance_coverage: number;
  patient_responsibility: number;
  deductible: number;
  copay: number;
  out_of_pocket_max: number;
  payment_plans: PaymentPlan[];
  calculated_at: string; // ISO 8601 datetime
  data_sources: string[];
}
```

### PaymentPlan
```typescript
{
  name: string;
  monthly_payment: number;
  duration_months: number;
  interest_rate: number;
  total_paid: number;
}
```

---

## Requirements Reference

This API documentation satisfies **Requirement 9.1**:
- All endpoints documented with request/response examples
- Authentication requirements clearly specified
- Error codes referenced with descriptions

