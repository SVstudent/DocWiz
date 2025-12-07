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
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   ├── api/                 # API routes
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── alembic/                 # Database migrations
└── pyproject.toml           # Poetry configuration
```
