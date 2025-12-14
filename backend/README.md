# DocWiz Backend

FastAPI backend for the DocWiz surgical visualization and cost estimation platform.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Start development services:
```bash
docker-compose up -d
```

4. Run database migrations:
```bash
poetry run alembic upgrade head
```

5. Start the development server:
```bash
poetry run uvicorn app.main:app --reload
```

6. (Optional) Start Celery worker for async tasks:
```bash
./start_celery_worker.sh
# Or manually:
poetry run celery -A celery_worker worker --loglevel=info --pool=solo
```

See [CELERY_SETUP.md](CELERY_SETUP.md) for detailed Celery configuration and usage.

## Development

### Code Formatting
```bash
poetry run black .
poetry run isort .
```

### Linting
```bash
poetry run flake8
poetry run mypy .
```

### Testing
```bash
poetry run pytest
poetry run pytest --cov=app tests/
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── celery_app.py        # Celery application configuration
│   ├── db/                  # Database models and seeds
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   ├── tasks/               # Celery async tasks
│   ├── api/                 # API routes
│   │   └── routes/          # API endpoints
│   │       ├── tasks.py     # Task status endpoints
│   │       └── websockets.py # WebSocket for real-time updates
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── celery_worker.py         # Celery worker entry point
├── start_celery_worker.sh   # Script to start Celery worker
├── CELERY_SETUP.md          # Celery documentation
└── pyproject.toml           # Poetry configuration
```

## Async Task Processing

DocWiz uses Celery for handling long-running operations:

- **Visualization Generation**: AI-powered surgical preview generation (5-30 seconds)
- **Comparison Generation**: Multi-procedure comparisons (10-60 seconds)
- **Export Generation**: Comprehensive report creation (5-20 seconds)
- **Cost Infographics**: Visual cost breakdown generation (3-10 seconds)

### Using Async Endpoints

API endpoints support both synchronous and asynchronous processing:

```bash
# Synchronous (waits for completion)
POST /api/visualizations?async_processing=false

# Asynchronous (returns task_id immediately)
POST /api/visualizations?async_processing=true
```

### Tracking Task Progress

```bash
# Get task status
GET /api/tasks/{task_id}/status

# WebSocket for real-time updates
WS /api/ws/tasks/{task_id}
```

See [CELERY_SETUP.md](CELERY_SETUP.md) for complete documentation.
