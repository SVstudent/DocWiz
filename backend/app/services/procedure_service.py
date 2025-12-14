"""Procedure service for managing surgical procedures.

This service provides methods to:
- Fetch all procedures
- Filter procedures by category
- Retrieve procedure details
- Initialize procedure data in Firestore
"""
from typing import List, Optional, Dict, Any
from google.cloud.firestore_v1 import Client

from app.db.firestore_models import ProcedureModel
from app.db.seed_procedures import (
    get_all_procedures,
    get_procedure_by_id as get_seed_procedure_by_id,
    get_procedures_by_category as get_seed_procedures_by_category,
    get_all_categories as get_seed_categories
)
from app.db.base import Collections


class ProcedureService:
    """Service for managing surgical procedures."""
    
    def __init__(self, db: Client):
        """Initialize procedure service.
        
        Args:
            db: Firestore client instance
        """
        self.db = db
        self.collection = Collections.PROCEDURES
    
    async def initialize_procedures(self) -> int:
        """Initialize procedures in Firestore from seed data.
        
        This method should be called once during application setup
        to populate the procedures collection with seed data.
        
        Returns:
            Number of procedures created
        """
        seed_procedures = get_all_procedures()
        count = 0
        
        for proc_data in seed_procedures:
            # Check if procedure already exists
            existing = self.db.collection(self.collection).document(proc_data["id"]).get()
            if not existing.exists:
                # Create procedure model
                procedure = ProcedureModel(**proc_data)
                # Store in Firestore
                self.db.collection(self.collection).document(procedure.id).set(
                    procedure.model_dump(mode='json')
                )
                count += 1
        
        return count
    
    async def get_all_procedures(self) -> List[ProcedureModel]:
        """Fetch all procedures from Firestore.
        
        Returns:
            List of all procedure models
        """
        docs = self.db.collection(self.collection).stream()
        procedures = []
        
        for doc in docs:
            data = doc.to_dict()
            if data:
                procedures.append(ProcedureModel(**data))
        
        return procedures
    
    async def get_procedure_by_id(self, procedure_id: str) -> Optional[ProcedureModel]:
        """Retrieve a specific procedure by ID.
        
        Args:
            procedure_id: Unique procedure identifier
        
        Returns:
            Procedure model if found, None otherwise
        """
        doc = self.db.collection(self.collection).document(procedure_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            if data:
                return ProcedureModel(**data)
        
        return None
    
    async def get_procedures_by_category(self, category: str) -> List[ProcedureModel]:
        """Filter procedures by category.
        
        Args:
            category: Procedure category (e.g., 'facial', 'body', 'reconstructive')
        
        Returns:
            List of procedures in the specified category
        """
        query = self.db.collection(self.collection).where("category", "==", category)
        docs = query.stream()
        
        procedures = []
        for doc in docs:
            data = doc.to_dict()
            if data:
                procedures.append(ProcedureModel(**data))
        
        return procedures
    
    async def get_all_categories(self) -> List[str]:
        """Get all unique procedure categories.
        
        Returns:
            List of unique category names
        """
        docs = self.db.collection(self.collection).stream()
        categories = set()
        
        for doc in docs:
            data = doc.to_dict()
            if data and "category" in data:
                categories.add(data["category"])
        
        return sorted(list(categories))
    
    async def search_procedures(self, query: str) -> List[ProcedureModel]:
        """Search procedures by name or description.
        
        Note: Firestore doesn't support full-text search natively.
        This is a simple implementation that filters by name prefix.
        For production, consider using Algolia or Elasticsearch.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching procedures
        """
        # Get all procedures and filter in memory
        # This is acceptable for small datasets
        all_procedures = await self.get_all_procedures()
        query_lower = query.lower()
        
        matching = []
        for proc in all_procedures:
            if (query_lower in proc.name.lower() or 
                query_lower in proc.description.lower()):
                matching.append(proc)
        
        return matching
    
    async def get_procedure_count(self) -> int:
        """Get total count of procedures.
        
        Returns:
            Total number of procedures in database
        """
        docs = self.db.collection(self.collection).stream()
        return sum(1 for _ in docs)


def get_procedure_service(db: Client) -> ProcedureService:
    """Factory function to create procedure service instance.
    
    Args:
        db: Firestore client
    
    Returns:
        ProcedureService instance
    """
    return ProcedureService(db)
