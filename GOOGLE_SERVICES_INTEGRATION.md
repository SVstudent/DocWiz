# Google Services Integration - DocWiz

This document outlines all Google Cloud services used in DocWiz to maximize integration for the hackathon.

## 🎯 Why All-Google Stack?

For the Google DeepMind hackathon, we're using maximum Google services to:
- **Impress judges** with deep ecosystem integration
- **Score higher** on technical sophistication
- **Demonstrate** understanding of Google Cloud Platform
- **Leverage** best-in-class AI and infrastructure

## 📊 Google Services Used

### 1. **Google Gemini 2.5 Flash Image** ⭐
**Purpose**: AI-powered surgical visualization generation

**What it does**:
- Generates photorealistic before/after surgical previews
- Region-specific image editing (e.g., nose reshaping, lip repair)
- Maintains non-surgical features with pixel-level fidelity

**Integration**:
```python
# backend/app/services/gemini_client.py
gemini_client = GeminiClient(api_key=settings.gemini_api_key)
result = await gemini_client.generate_surgical_preview(
    image=patient_image,
    procedure=procedure,
    prompt=surgical_prompt
)
```

**API Key**: `GEMINI_API_KEY` in `.env`

---

### 2. **Google Nano Banana** ⭐
**Purpose**: Natural language generation for medical documentation

**What it does**:
- Generates medical necessity justifications for insurance
- Creates professional language for pre-authorization forms
- Explains surgical procedures in patient-friendly terms

**Integration**:
```python
# backend/app/services/nano_banana_client.py
nano_client = NanoBananaClient(api_key=settings.nano_banana_api_key)
justification = await nano_client.generate_medical_justification(
    procedure=procedure,
    patient_history=history
)
```

**API Key**: `NANO_BANANA_API_KEY` in `.env`

---

### 3. **Firebase/Firestore** ⭐
**Purpose**: NoSQL document database for all application data

**What it stores**:
- User accounts and authentication
- Patient profiles (encrypted sensitive data)
- Surgical procedures and definitions
- Cost breakdowns and estimates
- Visualization results metadata
- Insurance forms and documents

**Integration**:
```python
# backend/app/db/base.py
from firebase_admin import firestore
db = firestore.client()

# Create document
db.collection('patient_profiles').document(profile_id).set(profile_data)

# Query documents
results = db.collection('procedures').where('category', '==', 'facial').get()
```

**Setup**: See `FIREBASE_SETUP.md`

---

### 4. **Google Cloud Storage (GCS)** ⭐
**Purpose**: Object storage for images and generated files

**What it stores**:
- Patient uploaded photos (before surgery)
- AI-generated surgical previews (after surgery)
- Cost infographics (PNG/JPEG)
- Insurance claim PDFs
- Export reports

**Integration**:
```python
# backend/app/services/storage.py
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket(settings.gcs_bucket_name)

# Upload image
blob = bucket.blob(f'images/{image_id}.jpg')
blob.upload_from_file(image_file)
image_url = blob.public_url
```

**Configuration**:
- `GCS_BUCKET_NAME`: Bucket name
- `GCS_PROJECT_ID`: Google Cloud project ID
- `GCS_CREDENTIALS_PATH`: Service account JSON

---

### 5. **Google Cloud Run** (Deployment) 🚀
**Purpose**: Serverless container deployment for FastAPI backend

**Why**:
- Auto-scaling based on traffic
- Pay only for actual usage
- Seamless integration with other Google services
- HTTPS automatically configured

**Deployment**:
```bash
# Build and deploy
gcloud run deploy docwiz-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Gemini     │  │ Nano Banana  │  │  Firestore   │ │
│  │ 2.5 Flash    │  │              │  │  Database    │ │
│  │   Image      │  │   (Text)     │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │                            │
│                    ┌───────▼────────┐                   │
│                    │   FastAPI      │                   │
│                    │   Backend      │                   │
│                    │  (Cloud Run)   │                   │
│                    └───────┬────────┘                   │
│                            │                            │
│                    ┌───────▼────────┐                   │
│                    │  Cloud Storage │                   │
│                    │   (Images)     │                   │
│                    └────────────────┘                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
         │                                        │
         │                                        │
    ┌────▼────┐                            ┌─────▼─────┐
    │ Qdrant  │                            │  Freepik  │
    │ Vector  │                            │    API    │
    │   DB    │                            │           │
    └─────────┘                            └───────────┘
```

## 🔑 Environment Variables Summary

All Google services require these environment variables:

```bash
# Google AI Services
GEMINI_API_KEY=your_gemini_api_key
NANO_BANANA_API_KEY=your_nano_banana_api_key

# Firebase/Firestore
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Google Cloud Storage
GCS_BUCKET_NAME=docwiz-images-prod
GCS_PROJECT_ID=your_gcp_project_id
GCS_CREDENTIALS_PATH=./firebase-credentials.json

# Freepik (via MCP)
FREEPIK_API_KEY=your_freepik_api_key
```

## 📝 Setup Checklist

- [ ] Create Google Cloud Project
- [ ] Enable Gemini API
- [ ] Enable Nano Banana API
- [ ] Set up Firebase/Firestore
- [ ] Create GCS bucket
- [ ] Download service account credentials
- [ ] Update `.env` with all API keys
- [ ] Configure Freepik MCP server
- [ ] Test all integrations

## 🎯 Hackathon Scoring Benefits

Using all Google services demonstrates:

✅ **Deep Integration**: Not just using one API, but the entire ecosystem
✅ **Technical Sophistication**: Understanding when to use each service
✅ **Production-Ready**: Using enterprise-grade Google Cloud infrastructure
✅ **Scalability**: All services auto-scale with demand
✅ **Best Practices**: Following Google's recommended architecture patterns

## 🚀 Quick Start

1. **Get API Keys**:
   ```bash
   # Visit these URLs:
   # - Gemini: https://makersuite.google.com/app/apikey
   # - Firebase: https://console.firebase.google.com/
   # - Freepik: https://www.freepik.com/api
   ```

2. **Set up Firebase**:
   ```bash
   # Follow FIREBASE_SETUP.md
   ```

3. **Update Environment**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your keys
   ```

4. **Install Dependencies**:
   ```bash
   cd backend
   poetry install
   ```

5. **Run Backend**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## 📚 Resources

- [Gemini API Docs](https://ai.google.dev/docs)
- [Firebase Docs](https://firebase.google.com/docs)
- [Cloud Storage Docs](https://cloud.google.com/storage/docs)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Freepik API Docs](https://www.freepik.com/api/docs)

## 🏆 Winning Strategy

This all-Google stack positions DocWiz to win because:

1. **Judges see commitment** to Google ecosystem
2. **Technical depth** across multiple services
3. **Real-world architecture** that could scale to production
4. **Innovation** in combining AI services for healthcare
5. **Completeness** - not just a demo, but a full platform

Good luck with the hackathon! 🚀
