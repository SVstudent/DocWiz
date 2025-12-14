#!/usr/bin/env python3
"""Initialize Qdrant collection."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.qdrant_client import QdrantClient


async def main():
    """Initialize Qdrant collection."""
    print("Initializing Qdrant collection...")
    
    try:
        client = QdrantClient()
        await client.ensure_collection_exists()
        print("✅ Qdrant collection 'surgical_embeddings' initialized successfully!")
        
        # Get collection info
        info = await client.get_collection_info()
        print(f"\nCollection Info:")
        print(f"  Points: {info.get('points_count', 0)}")
        print(f"  Vectors: {info.get('vectors_count', 0)}")
        print(f"  Status: {info.get('status', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Qdrant: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
