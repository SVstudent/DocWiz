# DocWiz - Surgical Visualization & Cost Estimation Platform

> 🏆 Built for the Google DeepMind Sketch & Search Hackathon with maximum Google Cloud integration

DocWiz is a comprehensive surgical visualization and cost estimation platform that helps patients make informed decisions about plastic and reconstructive surgeries. The system provides photorealistic previews of surgical outcomes using AI-powered image generation, detailed cost breakdowns with insurance calculations, and comparative analysis tools.

## 🌟 Features

- **AI-Powered Surgical Previews**: Photorealistic before/after visualizations using Google Gemini
- **AI Similarity Analysis**: Compare AI predictions with real results using multimodal AI
- **Cost Estimation**: Detailed cost breakdowns with insurance coverage calculations
- **Visual Infographics**: AI-generated cost breakdown graphics via Freepik
- **Similar Cases Search**: Vector similarity search to find matching surgical outcomes
- **Insurance Documentation**: Generate pre-authorization forms
- **Comprehensive Exports**: Export reports in multiple formats (PDF, PNG, JPEG, JSON)

---

## � Core AI & Technology Integrations

### 🤖 Google Gemini (Primary AI Engine)
DocWiz leverages **Google Gemini 2.0 Flash** as its core AI engine for multiple capabilities:

| Feature | Gemini Capability |
|---------|-------------------|
| **Surgical Visualization** | `gemini-2.0-flash` generates photorealistic before/after images of surgical outcomes |
| **Multimodal Analysis** | Compares AI-predicted results with real post-surgery photos using vision + text |
| **Medical Documentation** | Generates insurance pre-authorization forms and medical necessity letters |
| **Text Analysis** | Analyzes procedure details and patient information |

**Implementation**: `/backend/app/services/nano_banana_client.py`
- `generate_image()` - Creates surgical visualizations
- `generate_multimodal_analysis()` - Compares AI vs real results
- `generate_text()` - Creates medical documentation

---

### 🧠 Qdrant (Vector Similarity Search)
DocWiz uses **Qdrant** vector database to find similar surgical cases based on image embeddings:

| Component | Purpose |
|-----------|---------|
| **Image Embeddings** | 768-dimensional vectors representing surgical visualizations |
| **Similarity Search** | Find past cases visually similar to current patient |
| **Filtered Queries** | Filter by procedure type, age range, outcome quality |
| **Metadata Storage** | Store patient demographics (anonymized) with each case |

**How it works**:
```
Patient uploads image → Generate embedding → 
Search Qdrant for similar cases → Display matching outcomes
```

**Implementation**: `/backend/app/services/qdrant_client.py`, `/backend/app/services/embedding_service.py`

---

### 🎨 Freepik (Visual Asset Generation)
DocWiz integrates **Freepik's AI API** for generating professional cost infographics:

| Feature | Description |
|---------|-------------|
| **Cost Infographics** | Visual breakdown of surgical costs (surgeon fee, facility, anesthesia, etc.) |
| **Professional Styling** | Medical-themed designs with surgical blue color scheme |
| **Multiple Formats** | PNG/JPEG output for patient consultations |

**Example prompt generated**:
> "Create a professional medical cost breakdown infographic showing Total: $8,500, Surgeon Fee: $4,000..."

**Implementation**: `/backend/app/services/freepik_client.py`

---

### ☁️ Firebase/Google Cloud
- **Firestore** - NoSQL database for patients, procedures, visualizations
- **Cloud Storage** - Image and document storage
- **Authentication** - User auth via Firebase Auth

---

## 🚀 Technology Stack

### Backend
- FastAPI (Python 3.11+)
- Google Gemini 2.0 Flash (AI generation)
- Qdrant (vector similarity search)
- Freepik API (infographic generation)
- Firebase/Firestore (database)
- Redis + Celery (async processing)

### Frontend
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS
- Zustand + React Query

### Testing
- Hypothesis (property-based testing - 33 properties)
- pytest + Jest


## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Poetry (Python package manager)
- Firebase project with Firestore enabled

### Quick Start

**📖 See [SETUP_COMPLETE.md](SETUP_COMPLETE.md) for detailed setup instructions!**

1. **Get API Keys**:
   - Gemini: https://makersuite.google.com/app/apikey
   - Firebase: https://console.firebase.google.com/ (download credentials)
   - Freepik: https://www.freepik.com/api

2. **Clone and configure**:
```bash
git clone <repository-url>
cd docwiz

# Backend
cd backend
cp .env.example .env
# Edit .env with your API keys and Firebase project ID
# Place firebase-credentials.json in backend/

# Frontend
cd ../frontend
npm install
```

3. **Start services**:
```bash
# Start Firestore emulator, Qdrant, Redis
docker-compose up -d
```

4. **Run the application**:
```bash
# Backend
cd backend
poetry install
poetry run uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm run dev
```

5. **Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Firestore Emulator: http://localhost:8080

## Project Structure

```
docwiz/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Backend tests
│   └── alembic/            # Database migrations
├── frontend/               # Next.js frontend
│   ├── src/                # Source code
│   └── public/             # Static assets
├── docker-compose.yml      # Development services
└── README.md              # This file
```

## Development

### Backend Development

```bash
cd backend

# Format code
poetry run black .
poetry run isort .

# Lint
poetry run flake8
poetry run mypy .

# Run tests
poetry run pytest
poetry run pytest --cov=app tests/
```

### Frontend Development

```bash
cd frontend

# Format code
npm run format

# Lint
npm run lint

# Type check
npm run type-check

# Run tests
npm run test
npm run test:coverage
```

## Testing

The project uses a comprehensive testing strategy:

- **Unit Tests**: Test specific functionality and edge cases
- **Property-Based Tests**: Verify universal properties using Hypothesis (backend) and fast-check (frontend)
- **Integration Tests**: Test complete workflows with real services

Run all tests:
```bash
# Backend
cd backend && poetry run pytest

# Frontend
cd frontend && npm run test
```

## 📚 Documentation

### Setup Guides
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Complete setup overview
- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Firebase/Firestore configuration
- **[GOOGLE_SERVICES_INTEGRATION.md](GOOGLE_SERVICES_INTEGRATION.md)** - All Google services
- **[.kiro/settings/MCP_SETUP.md](.kiro/settings/MCP_SETUP.md)** - Freepik MCP configuration

### Spec Documents
- **[Requirements](.kiro/specs/docwiz-surgical-platform/requirements.md)** - 10 user stories, 50 acceptance criteria
- **[Design](.kiro/specs/docwiz-surgical-platform/design.md)** - Architecture + 33 correctness properties
- **[Tasks](.kiro/specs/docwiz-surgical-platform/tasks.md)** - 32 implementation tasks

### API Documentation
- [Backend API Docs](http://localhost:8000/docs) - Interactive Swagger UI
- [Database Layer](backend/app/db/README.md) - Firestore integration guide

## 🏆 Hackathon Strategy

DocWiz is designed to win the Google DeepMind hackathon by:

✅ **Maximum Google Integration** - 5 Google services working together
✅ **Production-Ready** - Scalable architecture with comprehensive testing
✅ **Real-World Impact** - Solves actual healthcare decision-making problems
✅ **Technical Depth** - AI, vector search, encryption, async processing
✅ **Complete Documentation** - Every component fully documented

### Key Differentiators
- **33 Correctness Properties** with property-based testing
- **Firebase/Firestore** instead of traditional SQL (better Google integration)
- **Qdrant Vector Search** for intelligent case matching
- **"Surgically Effective" Design** - clean, minimal, purposeful UI
- **HIPAA-Compliant** - encrypted sensitive data, secure architecture

## 📊 Project Status

- ✅ Complete spec (requirements, design, tasks)
- ✅ Firebase/Firestore integration
- ✅ All Google services configured
- ✅ Freepik MCP server set up
- ✅ Testing strategy defined
- 🚧 Implementation in progress (see tasks.md)

## 🤝 Contributing

This is a hackathon project. To contribute:

1. Review the [tasks.md](.kiro/specs/docwiz-surgical-platform/tasks.md)
2. Pick a task and click "Start task" in Kiro
3. Follow the spec requirements and design
4. Write tests for all new functionality
5. Submit for review

## 📝 License

Proprietary - All rights reserved

## 💬 Support

For questions or issues:
- Check [SETUP_COMPLETE.md](SETUP_COMPLETE.md) first
- Review relevant setup guides
- Contact the DocWiz team

---

**Built with ❤️ for the Google DeepMind Sketch & Search Hackathon**
