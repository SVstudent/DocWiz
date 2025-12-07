# DocWiz - Surgical Visualization & Cost Estimation Platform

DocWiz is a comprehensive surgical visualization and cost estimation platform that helps patients make informed decisions about plastic and reconstructive surgeries. The system provides photorealistic previews of surgical outcomes using AI-powered image generation, detailed cost breakdowns with insurance calculations, and comparative analysis tools.

## Features

- **AI-Powered Surgical Previews**: Photorealistic before/after visualizations using Google Gemini 2.5 Flash Image
- **Cost Estimation**: Detailed cost breakdowns with insurance coverage calculations
- **Procedure Comparison**: Side-by-side comparison of multiple surgical options
- **Similar Cases Search**: Find similar procedures using vector similarity search
- **Insurance Documentation**: Generate pre-authorization forms and claim documentation
- **Comprehensive Exports**: Export reports in multiple formats (PDF, PNG, JPEG, JSON)

## Technology Stack

### Frontend
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS
- Zustand for state management
- React Query for server state

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL for data storage
- Qdrant for vector search
- Redis for caching and task queue
- Celery for async processing

### AI Services
- Google Gemini 2.5 Flash Image
- Google Nano Banana
- Freepik Studio API

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Poetry (Python package manager)

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd docwiz
```

2. Start development services:
```bash
docker-compose up -d
```

3. Set up the backend:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

4. Set up the frontend:
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

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

## Documentation

- [Backend API Documentation](http://localhost:8000/docs) - Interactive API documentation
- [Requirements Document](.kiro/specs/docwiz-surgical-platform/requirements.md)
- [Design Document](.kiro/specs/docwiz-surgical-platform/design.md)
- [Implementation Tasks](.kiro/specs/docwiz-surgical-platform/tasks.md)

## License

Proprietary - All rights reserved

## Support

For questions or issues, please contact the DocWiz team.
