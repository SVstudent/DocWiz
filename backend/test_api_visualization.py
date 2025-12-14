#!/usr/bin/env python3
"""Test the actual visualization API endpoint."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from PIL import Image
from io import BytesIO

# Test the service directly
async def test_visualization_service():
    """Test the visualization service directly."""
    from app.services.visualization_service import VisualizationService
    from app.services.storage_service import StorageService
    
    print("=" * 70)
    print("Testing Visualization Service Directly")
    print("=" * 70)
    
    # Create a test image
    test_image = Image.new('RGB', (512, 512), color='lightblue')
    image_bytes = BytesIO()
    test_image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    
    # Upload the test image
    storage_service = StorageService()
    image_id, image_url = storage_service.upload_image(
        image_bytes,
        "image/jpeg",
        "test_visualization.jpg"
    )
    print(f"✅ Uploaded test image: {image_id}")
    print(f"   URL: {image_url}")
    
    # Save image metadata to Firestore
    from app.db.base import get_db, Collections
    db = get_db()
    db.collection(Collections.IMAGES).document(image_id).set({
        "id": image_id,
        "url": image_url,
        "format": "JPEG",
        "width": 512,
        "height": 512,
        "size": len(image_bytes.getvalue()),
        "mime_type": "image/jpeg",
    })
    print(f"✅ Saved image metadata to Firestore")
    
    # Test visualization generation
    viz_service = VisualizationService()
    
    try:
        print("\n📤 Generating visualization...")
        result = await viz_service.generate_surgical_preview(
            image_id=image_id,
            procedure_id="rhinoplasty-001",  # Use a known procedure ID
            patient_id=None
        )
        
        print("\n✅ Visualization generated successfully!")
        print(f"   Visualization ID: {result['id']}")
        print(f"   Before URL: {result['before_image_url']}")
        print(f"   After URL: {result['after_image_url']}")
        print(f"   Model: {result['metadata']['model']}")
        
    except Exception as e:
        print(f"\n❌ Visualization generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_visualization_service())
