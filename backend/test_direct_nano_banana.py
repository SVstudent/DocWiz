#!/usr/bin/env python3
"""Test NanoBanana client directly with the same approach as test_prompt_and_image.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from PIL import Image
from io import BytesIO

async def test_nano_banana_direct():
    """Test NanoBanana client directly."""
    from app.services.nano_banana_client import NanoBananaClient
    
    print("=" * 70)
    print("Testing NanoBanana Client Directly")
    print("=" * 70)
    
    # Create a test image
    test_image = Image.new('RGB', (512, 512), color='lightblue')
    image_bytes = BytesIO()
    test_image.save(image_bytes, format='JPEG')
    image_data = image_bytes.getvalue()
    
    print(f"✅ Created test image: {len(image_data)} bytes")
    
    # Initialize client
    client = NanoBananaClient()
    print(f"✅ Client initialized")
    print(f"   Image model: {client.image_model}")
    
    # Test image editing
    prompt = "rhinoplasty surgery. The nose should be straighter and more refined"
    
    try:
        print(f"\n📤 Calling edit_image with prompt: {prompt[:50]}...")
        result = await client.edit_image(
            image_data=image_data,
            prompt=prompt,
            mime_type="image/jpeg"
        )
        
        print(f"\n✅ Image editing successful!")
        print(f"   Result size: {len(result)} bytes")
        
    except Exception as e:
        print(f"\n❌ Image editing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nano_banana_direct())
