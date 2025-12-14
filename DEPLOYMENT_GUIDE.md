# DocWiz Deployment Guide

## Overview

This guide covers deploying the DocWiz surgical visualization platform in development, staging, and production environments. DocWiz consists of:

- **Backend API**: FastAPI Python application
- **Frontend**: Next.js React application
- **Dependencies**: Firestore, Qdrant, Redis, Celery workers

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker** 20.10+ and Docker Compose 2.0+
- **Python** 3.11+
- **Node.js** 18+ and npm 9+
- **Poetry** 1.6+ (Python package manager)
- **Git** 2.30+

### Required Services

- **Google Cloud Platform** account with:
  - Firebase/Firestore enabled
  - Cloud Storage bucket created
  - Service account with credentials
- **Google AI** API keys:
  - Gemini API key
  - Nano Banana API key (same as Gemini)
- **Freepik API** key (optional, for enhanced visualizations)

### System Requirements

**Development:**
- 8GB RAM minimum
- 20GB disk space
- Multi-core CPU recommended

**Production:**
- 16GB RAM minimum
- 100GB disk space
- 4+ CPU cores
- Load balancer (for high availability)


---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env` from `backend/.env.example`:

```bash
cd backend
cp .env.example .env
```

**Required Variables:**

```bash
# Firebase/Firestore Database
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# For local development with emulator
FIRESTORE_EMULATOR_HOST=localhost:8080
USE_FIRESTORE_EMULATOR=true  # Set to false for production

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=surgical_embeddings

# Google AI Services
GEMINI_API_KEY=your_gemini_api_key
NANO_BANANA_API_KEY=your_gemini_api_key  # Same as Gemini

# Freepik API (optional)
FREEPIK_API_KEY=your_freepik_api_key

# Google Cloud Storage
GCS_BUCKET_NAME=docwiz-images-prod
GCS_PROJECT_ID=your_gcp_project_id
GCS_CREDENTIALS_PATH=./firebase-credentials.json

# Security (IMPORTANT: Generate secure keys for production)
SECRET_KEY=generate_a_secure_random_key_minimum_32_characters
ENCRYPTION_KEY=generate_a_32_character_encryption_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
ENVIRONMENT=production  # development, staging, or production
DEBUG=false  # Set to false in production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Generating Secure Keys:**

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (must be 32 bytes)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Frontend Environment Variables

Create `frontend/.env.local` from `frontend/.env.example`:

```bash
cd frontend
cp .env.example .env.local
```

**Required Variables:**

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000  # Change to production URL
NEXT_PUBLIC_API_TIMEOUT=30000

# Environment
NEXT_PUBLIC_ENVIRONMENT=production

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_ERROR_REPORTING=true
```

### Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file as `backend/firebase-credentials.json`

**Important:** Never commit this file to version control!


---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/docwiz.git
cd docwiz
```

### 2. Start Infrastructure Services

Start Firestore emulator, Qdrant, and Redis using Docker Compose:

```bash
docker-compose up -d
```

Verify services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                  STATUS    PORTS
docwiz-firestore      Up        0.0.0.0:8080->8080/tcp
docwiz-qdrant         Up        0.0.0.0:6333->6333/tcp, 0.0.0.0:6334->6334/tcp
docwiz-redis          Up        0.0.0.0:6379->6379/tcp
```

### 3. Setup Backend

```bash
cd backend

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Add Firebase credentials
# Place firebase-credentials.json in backend/ directory

# Initialize database (seed procedures and pricing data)
poetry run python -m app.db.seed_procedures
poetry run python -m app.db.seed_pricing

# Run database migrations (if using PostgreSQL)
# poetry run alembic upgrade head

# Start backend server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 4. Setup Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 5. Start Celery Worker (Optional)

For async task processing, open another terminal:

```bash
cd backend
poetry shell

# Start Celery worker
poetry run celery -A celery_worker worker --loglevel=info --pool=solo
```

### 6. Verify Installation

1. Open `http://localhost:3000` in your browser
2. Register a new user account
3. Create a patient profile
4. Upload an image
5. Generate a surgical visualization


---

## Docker Deployment

### Full Stack Docker Setup

Create a production `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: docwiz-backend
    ports:
      - "8000:8000"
    environment:
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - NANO_BANANA_API_KEY=${NANO_BANANA_API_KEY}
      - FREEPIK_API_KEY=${FREEPIK_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - ENVIRONMENT=production
      - DEBUG=false
    volumes:
      - ./backend/firebase-credentials.json:/app/firebase-credentials.json:ro
    depends_on:
      - redis
      - qdrant
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    container_name: docwiz-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_ENVIRONMENT=production
    depends_on:
      - backend
    restart: unless-stopped

  # Celery Worker
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: docwiz-celery-worker
    command: poetry run celery -A celery_worker worker --loglevel=info --concurrency=4
    environment:
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - NANO_BANANA_API_KEY=${NANO_BANANA_API_KEY}
      - FREEPIK_API_KEY=${FREEPIK_API_KEY}
    volumes:
      - ./backend/firebase-credentials.json:/app/firebase-credentials.json:ro
    depends_on:
      - redis
      - qdrant
    restart: unless-stopped

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: docwiz-qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    container_name: docwiz-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: docwiz-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  qdrant_data:
  redis_data:
```

### Backend Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile.prod`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build arguments
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build application
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
```

### Deploy with Docker

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes
docker-compose -f docker-compose.prod.yml down -v
```


---

## Production Deployment

### Cloud Platform Options

#### Option 1: Google Cloud Platform (Recommended)

**Services Used:**
- Cloud Run (Backend API)
- Cloud Run (Frontend)
- Cloud Run (Celery Workers)
- Firestore (Database)
- Cloud Storage (Images)
- Memorystore for Redis
- Qdrant Cloud or self-hosted on GCE

**Deployment Steps:**

1. **Setup GCP Project**

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize and authenticate
gcloud init
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

2. **Deploy Backend to Cloud Run**

```bash
cd backend

# Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/docwiz-backend

# Deploy to Cloud Run
gcloud run deploy docwiz-backend \
  --image gcr.io/YOUR_PROJECT_ID/docwiz-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=YOUR_PROJECT_ID \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-secrets SECRET_KEY=secret-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

3. **Deploy Frontend to Cloud Run**

```bash
cd frontend

# Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/docwiz-frontend \
  --build-arg NEXT_PUBLIC_API_URL=https://docwiz-backend-xxx.run.app

# Deploy to Cloud Run
gcloud run deploy docwiz-frontend \
  --image gcr.io/YOUR_PROJECT_ID/docwiz-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1
```

4. **Setup Custom Domain**

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service docwiz-frontend \
  --domain www.yourdomain.com \
  --region us-central1
```

#### Option 2: AWS Deployment

**Services Used:**
- ECS/Fargate (Containers)
- RDS (Database alternative)
- S3 (Storage)
- ElastiCache (Redis)
- EC2 (Qdrant)

**Deployment Steps:**

1. **Create ECR Repositories**

```bash
# Create repositories
aws ecr create-repository --repository-name docwiz-backend
aws ecr create-repository --repository-name docwiz-frontend

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

2. **Build and Push Images**

```bash
# Backend
cd backend
docker build -t docwiz-backend -f Dockerfile.prod .
docker tag docwiz-backend:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/docwiz-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/docwiz-backend:latest

# Frontend
cd frontend
docker build -t docwiz-frontend -f Dockerfile.prod .
docker tag docwiz-frontend:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/docwiz-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/docwiz-frontend:latest
```

3. **Create ECS Task Definitions and Services**

Use AWS Console or CLI to create ECS task definitions and services for backend, frontend, and Celery workers.

#### Option 3: DigitalOcean App Platform

**Deployment Steps:**

1. **Create App**

```bash
# Install doctl
brew install doctl  # macOS
# or download from https://docs.digitalocean.com/reference/doctl/

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml
```

2. **App Spec File** (`.do/app.yaml`)

```yaml
name: docwiz
services:
  - name: backend
    github:
      repo: your-org/docwiz
      branch: main
      deploy_on_push: true
    dockerfile_path: backend/Dockerfile.prod
    http_port: 8000
    instance_count: 2
    instance_size_slug: professional-s
    envs:
      - key: ENVIRONMENT
        value: production
      - key: FIREBASE_PROJECT_ID
        value: ${FIREBASE_PROJECT_ID}
      - key: GEMINI_API_KEY
        value: ${GEMINI_API_KEY}
        type: SECRET
  
  - name: frontend
    github:
      repo: your-org/docwiz
      branch: main
      deploy_on_push: true
    dockerfile_path: frontend/Dockerfile.prod
    http_port: 3000
    instance_count: 2
    instance_size_slug: basic-s
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: ${backend.PUBLIC_URL}

databases:
  - name: redis
    engine: REDIS
    version: "7"
```


---

### SSL/TLS Configuration

#### Using Let's Encrypt with Nginx

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # API endpoints
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Frontend
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**Generate SSL Certificates:**

```bash
# Install Certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Setup auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring and Maintenance

### Health Checks

**Backend Health Endpoint:**

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "firestore": "connected",
    "redis": "connected",
    "qdrant": "connected"
  }
}
```

### Logging

**View Docker Logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

**Application Logs:**

Backend logs are written to stdout/stderr and can be collected by:
- Docker logging drivers
- Cloud platform logging (Cloud Logging, CloudWatch)
- Log aggregation tools (ELK Stack, Datadog, Splunk)

### Monitoring Tools

**Recommended Monitoring Stack:**

1. **Prometheus + Grafana**
   - Metrics collection and visualization
   - Custom dashboards for API performance
   - Alert rules for critical issues

2. **Sentry**
   - Error tracking and reporting
   - Performance monitoring
   - User feedback collection

3. **Uptime Monitoring**
   - UptimeRobot
   - Pingdom
   - StatusCake

### Backup Strategy

**Firestore Backups:**

```bash
# Export Firestore data
gcloud firestore export gs://YOUR_BACKUP_BUCKET/firestore-backup-$(date +%Y%m%d)

# Schedule daily backups with Cloud Scheduler
gcloud scheduler jobs create http firestore-backup \
  --schedule="0 2 * * *" \
  --uri="https://firestore.googleapis.com/v1/projects/YOUR_PROJECT_ID/databases/(default):exportDocuments" \
  --message-body='{"outputUriPrefix":"gs://YOUR_BACKUP_BUCKET/scheduled-backups"}' \
  --oauth-service-account-email=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

**Qdrant Backups:**

```bash
# Create snapshot
curl -X POST 'http://localhost:6333/collections/surgical_embeddings/snapshots'

# Download snapshot
curl -X GET 'http://localhost:6333/collections/surgical_embeddings/snapshots/SNAPSHOT_NAME' \
  --output snapshot.tar
```

### Database Maintenance

**Qdrant Collection Optimization:**

```bash
# Optimize collection
curl -X POST 'http://localhost:6333/collections/surgical_embeddings/optimize'
```

**Redis Maintenance:**

```bash
# Check memory usage
redis-cli INFO memory

# Clear cache (if needed)
redis-cli FLUSHDB
```


---

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Symptom:** Backend fails to start with connection errors

**Solutions:**

```bash
# Check if all services are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Verify environment variables
cd backend
cat .env

# Test Firestore connection
poetry run python test_firebase_connection.py

# Test Redis connection
redis-cli ping

# Test Qdrant connection
curl http://localhost:6333/health
```

#### 2. Frontend Can't Connect to Backend

**Symptom:** Frontend shows "Network Error" or "Failed to fetch"

**Solutions:**

```bash
# Check NEXT_PUBLIC_API_URL in frontend/.env.local
cat frontend/.env.local

# Verify backend is accessible
curl http://localhost:8000/health

# Check CORS settings in backend/.env
# Ensure frontend URL is in CORS_ORIGINS

# Check browser console for specific errors
# Open DevTools → Console
```

#### 3. Image Upload Fails

**Symptom:** Image upload returns 400 or 500 error

**Solutions:**

```bash
# Check GCS bucket permissions
gsutil ls gs://YOUR_BUCKET_NAME

# Verify Firebase credentials
cat backend/firebase-credentials.json

# Check file size (max 10MB)
# Check file format (JPEG, PNG, WebP only)

# Test storage service
poetry run python -c "from app.services.storage_service import storage_service; print(storage_service.test_connection())"
```

#### 4. Celery Tasks Not Processing

**Symptom:** Async tasks stuck in "processing" state

**Solutions:**

```bash
# Check Celery worker is running
ps aux | grep celery

# Check Redis connection
redis-cli ping

# View Celery logs
tail -f celery.log

# Restart Celery worker
pkill -f celery
cd backend
poetry run celery -A celery_worker worker --loglevel=info --pool=solo
```

#### 5. Qdrant Vector Search Fails

**Symptom:** Similar cases search returns empty or errors

**Solutions:**

```bash
# Check Qdrant is running
curl http://localhost:6333/health

# Check collection exists
curl http://localhost:6333/collections/surgical_embeddings

# Verify embeddings are stored
curl http://localhost:6333/collections/surgical_embeddings/points/count

# Recreate collection if needed
curl -X DELETE http://localhost:6333/collections/surgical_embeddings
# Then restart backend to recreate
```

#### 6. Authentication Errors

**Symptom:** 401 Unauthorized errors

**Solutions:**

```bash
# Check JWT token expiration
# Tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES (default 60)

# Verify SECRET_KEY is set correctly
grep SECRET_KEY backend/.env

# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Check token in browser
# Open DevTools → Application → Local Storage
# Look for auth token
```

### Performance Issues

#### Slow API Responses

**Diagnosis:**

```bash
# Check backend logs for slow queries
docker-compose logs backend | grep "slow"

# Monitor Redis cache hit rate
redis-cli INFO stats | grep keyspace

# Check Qdrant query performance
curl http://localhost:6333/metrics
```

**Solutions:**

- Enable Redis caching for frequently accessed data
- Optimize Qdrant collection (run optimize endpoint)
- Increase backend instance resources
- Add database indexes for common queries
- Use CDN for static assets

#### High Memory Usage

**Diagnosis:**

```bash
# Check Docker container memory
docker stats

# Check Python memory usage
poetry run python -m memory_profiler app/main.py
```

**Solutions:**

- Increase container memory limits
- Optimize image processing (reduce resolution)
- Clear Redis cache periodically
- Limit concurrent Celery workers
- Use pagination for large result sets

### Getting Help

**Resources:**

- **Documentation:** Check README.md and API_DOCUMENTATION.md
- **Logs:** Always check application logs first
- **Health Checks:** Use `/health` endpoint to verify service status
- **Community:** GitHub Issues, Stack Overflow
- **Support:** Contact support@docwiz.com

**When Reporting Issues:**

Include:
1. Environment (development, staging, production)
2. Docker/service versions
3. Error messages and stack traces
4. Steps to reproduce
5. Relevant logs
6. Configuration (sanitized, no secrets)

---

## Requirements Reference

This deployment guide satisfies **Requirements 8.1 and 9.5**:
- Docker setup documented
- Environment variable configuration detailed
- Production deployment steps provided
- Multiple cloud platform options covered
- Monitoring and maintenance procedures included

