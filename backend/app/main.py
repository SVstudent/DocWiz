"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    auth,
    costs,
    exports,
    images,
    insurance,
    procedures,
    profiles,
    tasks,
    visualizations,
    websockets,
)
from app.config import settings
from app.db.base import initialize_firestore

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Surgical visualization and cost estimation platform",
    version=settings.app_version,
    debug=settings.debug,
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize Firebase/Firestore
    initialize_firestore()
    print("Firebase/Firestore initialized successfully")
    
    # Initialize Qdrant collection
    try:
        from app.services.qdrant_client import QdrantClient
        qdrant = QdrantClient()
        await qdrant.ensure_collection_exists()
        print("Qdrant collection initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize Qdrant: {e}")
        print("Qdrant features will be unavailable")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(procedures.router, prefix="/api")
app.include_router(visualizations.router, prefix="/api")
app.include_router(costs.router, prefix="/api")
app.include_router(insurance.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(websockets.router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "DocWiz API - Surgical Visualization Platform", "version": settings.app_version}
