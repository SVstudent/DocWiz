# DocWiz Google Cloud Deployment Guide

> Deploy the entire DocWiz platform on Google Cloud for maximum hackathon points! 🏆

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Firebase Project** (you likely already have this)
3. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
4. **Firebase CLI** installed: `npm install -g firebase-tools`

---

## Step 1: Initial Setup

### 1.1 Login to Google Cloud & Firebase
```bash
# Login to gcloud
gcloud auth login

# Login to Firebase
firebase login

# Set your project
gcloud config set project YOUR_PROJECT_ID
firebase use YOUR_PROJECT_ID
```

### 1.2 Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com
```

---

## Step 2: Deploy Backend to Cloud Run

### 2.1 Create Dockerfile for Backend
Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev dependencies, no virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2.2 Create .dockerignore
Create `backend/.dockerignore`:
```
__pycache__
*.pyc
*.pyo
.env
.git
.gitignore
tests/
*.md
.pytest_cache
.mypy_cache
```

### 2.3 Set Environment Variables
Create a `.env.yaml` file for Cloud Run (DO NOT commit this!):
```yaml
GEMINI_API_KEY: "your-gemini-api-key"
FREEPIK_API_KEY: "your-freepik-api-key"
FIREBASE_PROJECT_ID: "your-project-id"
GOOGLE_CLOUD_PROJECT: "your-project-id"
QDRANT_HOST: "your-qdrant-cloud-host"
QDRANT_PORT: "6333"
QDRANT_API_KEY: "your-qdrant-api-key"
```

### 2.4 Deploy to Cloud Run
```bash
cd backend

# Build and deploy in one command
gcloud run deploy docwiz-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --env-vars-file .env.yaml

# Note the URL output, e.g.: https://docwiz-backend-xxxxx-uc.a.run.app
```

---

## Step 3: Deploy Frontend to Firebase Hosting

### 3.1 Initialize Firebase Hosting
```bash
cd frontend

# Initialize Firebase (select Hosting)
firebase init hosting
# - Select your project
# - Public directory: out (for static export) OR .next (for SSR)
# - Single-page app: Yes
# - Overwrite index.html: No
```

### 3.2 Update Frontend Environment
Create/update `frontend/.env.production`:
```env
NEXT_PUBLIC_API_URL=https://docwiz-backend-xxxxx-uc.a.run.app
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
```

### 3.3 Build and Deploy
```bash
cd frontend

# Build for production
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

Your frontend will be live at: `https://YOUR_PROJECT_ID.web.app`

---

## Step 4: Set Up Supporting Services

### 4.1 Qdrant Cloud (Free Tier)
1. Go to https://cloud.qdrant.io/
2. Create a free cluster
3. Copy the URL and API key
4. Update your Cloud Run env vars:
```bash
gcloud run services update docwiz-backend \
  --region us-central1 \
  --update-env-vars "QDRANT_HOST=your-cluster.cloud.qdrant.io,QDRANT_API_KEY=your-key"
```

### 4.2 Firestore (Already Set Up)
Your Firestore is already cloud-hosted. Just make sure:
- Production mode rules are configured
- Indexes are deployed: `firebase deploy --only firestore:indexes`

---

## Step 5: Configure CORS

Update `backend/app/main.py` to allow your Firebase domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://YOUR_PROJECT_ID.web.app",
        "https://YOUR_PROJECT_ID.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend:
```bash
gcloud run deploy docwiz-backend --source . --region us-central1
```

---

## Step 6: Verify Deployment

1. **Frontend**: Visit `https://YOUR_PROJECT_ID.web.app`
2. **Backend**: Visit `https://docwiz-backend-xxxxx-uc.a.run.app/docs`
3. **Test the flow**: Upload image → Generate visualization → Compare

---

## Quick Reference

| Component | URL |
|-----------|-----|
| Frontend | `https://YOUR_PROJECT_ID.web.app` |
| Backend API | `https://docwiz-backend-xxxxx.run.app` |
| API Docs | `https://docwiz-backend-xxxxx.run.app/docs` |
| Firestore Console | `https://console.firebase.google.com/project/YOUR_PROJECT_ID/firestore` |

---

## Troubleshooting

### Backend not starting?
```bash
# Check logs
gcloud run logs read --service docwiz-backend --region us-central1
```

### CORS errors?
- Verify your frontend domain is in the `allow_origins` list
- Redeploy backend after changes

### Firebase deploy fails?
```bash
# Check Firebase project
firebase projects:list
firebase use YOUR_PROJECT_ID
```

---

## Cost Estimate (Free Tier)

| Service | Free Tier |
|---------|-----------|
| Cloud Run | 2M requests/month |
| Firebase Hosting | 10 GB/month |
| Firestore | 50K reads, 20K writes/day |
| Cloud Storage | 5 GB |
| Qdrant Cloud | 1 GB free cluster |

**For a hackathon demo, you'll stay well within free tiers!** 🎉
