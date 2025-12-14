"""Check the status of a visualization in Firestore."""
import asyncio
from app.db.base import get_db, Collections
from app.db.firestore_models import get_document

async def check_viz():
    viz_id = "38e331bf-480a-4601-bf40-67bf7571b389"
    
    db = get_db()
    viz_data = await get_document(db, Collections.VISUALIZATIONS, viz_id)
    
    if viz_data:
        print(f"Visualization found:")
        print(f"  ID: {viz_data.get('id')}")
        print(f"  Status: {viz_data.get('status', 'N/A')}")
        print(f"  Before Image: {viz_data.get('before_image_url', 'N/A')}")
        print(f"  After Image: {viz_data.get('after_image_url', 'N/A')}")
        print(f"  Generated At: {viz_data.get('generated_at', 'N/A')}")
        print(f"  Confidence: {viz_data.get('confidence_score', 'N/A')}")
        print(f"\nFull data:")
        import json
        print(json.dumps(viz_data, indent=2, default=str))
    else:
        print(f"Visualization {viz_id} not found in Firestore")
        print("\nThis means the visualization was never created.")
        print("The POST request likely failed or is still processing synchronously.")

if __name__ == "__main__":
    asyncio.run(check_viz())
