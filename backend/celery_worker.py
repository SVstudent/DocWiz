"""Celery worker startup script."""
import logging
from app.celery_app import celery_app
from app.db.base import initialize_firestore

# Import tasks to ensure they're registered
from app.tasks import visualization_tasks, export_tasks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Firebase/Firestore on worker startup
try:
    initialize_firestore()
    logger.info("Firebase/Firestore initialized successfully in Celery worker")
except Exception as e:
    logger.error(f"Failed to initialize Firebase/Firestore: {e}")

if __name__ == "__main__":
    # Start the Celery worker
    celery_app.start()
