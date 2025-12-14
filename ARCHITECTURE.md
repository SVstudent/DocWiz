# DocWiz Architecture - Google Cloud First

## Overview

DocWiz leverages Google Cloud Platform as the primary infrastructure provider, integrated with sponsor AI services (Freepik, Qdrant) for specialized capabilities.

## Technology Stack

### **Google Cloud Services (Primary)**

1. **Google Gemini 2.5 Flash Image** - Core AI for surgical visualization
   - Generates photorealistic "after" images from patient photos
   - Region-specific editing capabilities
   - Fast inference times (<10 seconds)

2. **Google Nano Banana** - Natural language generation
   - Medical necessity justifications for insurance claims
   - Professional documentation generation
   - HIPAA-compliant text generation

3. **Google Cloud Storage (GCS)** - Object storage
   - Patient photo uploads
   - Generated surgical visualization images
   - Exported PDFs and reports
   - CDN integration for fast delivery
   - HIPAA-compliant storage options

4. **Google Cloud SQL (PostgreSQL)** - Relational database
   - Patient profiles and medical data
   - Procedure definitions and pricing
   - Cost breakdowns and insurance data
   - Encrypted sensitive fields

5. **Google Cloud Run** - Container hosting (production)
   - FastAPI backend deployment
   - Auto-scaling based on demand
   - Pay-per-use pricing

6. **Google Cloud Memorystore (Redis)** - Caching and task queue
   - Session management
   - Celery task queue for async operations
   - API response caching

### **Sponsor AI Services (Integrated)**

1. **Freepik Studio API** - Enhanced visual content
   - Cost infographic generation (PNG/JPEG)
   - Image-to-video capabilities (healing progression)
   - Additional creative assets
   - Brand-safe content generation

2. **Qdrant Vector Database** - Similarity search
   - Visual embeddings for surgical results
   - Find similar cases by facial features, age, procedure
   - Self-hosted on Google Compute Engine
   - Fast vector similarity search

### **Frontend**

- **Vercel** (Next.js deployment) - Optimal for React/Next.js
- **Next.js 14** with App Router
- **Tailwind CSS** for styling
- **React Query** for server state

## Data Flow

### Surgical Visualization Workflow

```
1. Patient uploads photo → Google Cloud Storage
2. Photo + procedure selection → Google Gemini 2.5 Flash Image
3. Gemini generates "after" image → Google Cloud Storage
4. Generate embedding → Qdrant (for similarity search)
5. Display before/after to user
```

### Cost Estimation Workflow

```
1. Patient profile + procedure → Cost calculation service
2. Generate cost breakdown (surgeon, facility, anesthesia, post-op)
3. Calculate insurance coverage
4. Generate visual infographic → Freepik Studio API
5. Store results → Google Cloud SQL
6. Display to user
```

### Insurance Claim Workflow

```
1. Procedure + patient data → Claim generation service
2. Generate medical justification → Google Nano Banana
3. Format claim document (PDF + JSON)
4. Store → Google Cloud Storage
5. Provide download link to user
```

### Similar Cases Search

```
1. Patient photo → Generate embedding
2. Query Qdrant with filters (procedure, age, outcome quality)
3. Return top N similar cases
4. Display anonymized results to user
```

## Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vercel)                        │
│                    Next.js 14 + React                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Google Cloud Run)                      │
│                   FastAPI + Python                           │
└─┬───────────┬──────────┬──────────┬────────────┬───────────┘
  │           │          │          │            │
  ▼           ▼          ▼          ▼            ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ Gemini │ │ Nano │ │Freepik │ │ Qdrant │ │   GCS    │
│  2.5   │ │Banana│ │ Studio │ │(GCE VM)│ │ Storage  │
│ Flash  │ │      │ │  API   │ │        │ │          │
└────────┘ └──────┘ └────────┘ └────────┘ └──────────┘
  Google    Google    Sponsor    Sponsor     Google
     │         │          │          │           │
     └─────────┴──────────┴──────────┴───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Google Cloud SQL    │
              │    (PostgreSQL)      │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Google Memorystore   │
              │      (Redis)         │
              └──────────────────────┘
```

## Service Integration Summary

### Google Services (Primary Infrastructure)
- ✅ **Gemini 2.5 Flash Image** - Surgical visualization AI
- ✅ **Nano Banana** - Medical text generation
- ✅ **Cloud Storage** - Image and file storage
- ✅ **Cloud SQL** - PostgreSQL database
- ✅ **Cloud Run** - Backend hosting
- ✅ **Memorystore** - Redis caching

### Sponsor Services (Specialized AI)
- ✅ **Freepik Studio** - Visual content and infographics
- ✅ **Qdrant** - Vector similarity search

### Why This Architecture?

1. **Google-First**: Maximizes use of Google Cloud ecosystem
2. **Sponsor Integration**: Leverages Freepik and Qdrant for specialized capabilities
3. **Scalability**: All services auto-scale based on demand
4. **HIPAA Compliance**: Google Cloud offers HIPAA-compliant options
5. **Cost Efficiency**: Pay-per-use pricing for most services
6. **Performance**: Low latency with services in same cloud provider

## Environment Variables

```bash
# Google AI Services
GEMINI_API_KEY=your_gemini_api_key
NANO_BANANA_API_KEY=your_nano_banana_api_key

# Sponsor AI Services
FREEPIK_API_KEY=your_freepik_api_key
QDRANT_HOST=your_qdrant_host
QDRANT_PORT=6333

# Google Cloud Storage
GCS_BUCKET_NAME=docwiz-images
GCS_PROJECT_ID=your-gcp-project-id
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json

# Google Cloud SQL
DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance

# Google Memorystore (Redis)
REDIS_URL=redis://10.x.x.x:6379/0
```

## Deployment

### Development
- Local PostgreSQL + Redis via Docker Compose
- Qdrant via Docker
- Google Cloud APIs via API keys

### Production
- Google Cloud Run for backend
- Google Cloud SQL for database
- Google Memorystore for Redis
- Qdrant on Google Compute Engine VM
- Vercel for frontend

## Cost Optimization

- Use Google Cloud free tier where possible
- Implement caching to reduce API calls
- Use Cloud Storage lifecycle policies
- Monitor usage with Google Cloud Monitoring
- Set up budget alerts
