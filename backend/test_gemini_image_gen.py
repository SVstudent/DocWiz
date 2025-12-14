#!/usr/bin/env python3
"""Test script for Gemini 2.0 Flash + Imagen 3 image generation."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.nano_banana_client import NanoBananaClient
from PIL import Image
from io import BytesIO


async def test_image_generation():
    """Test image generation with a sample image."""
    print("🧪 Testing Gemini 2.0 Flash + Imagen 3 image generation...")
    
    # Initialize client
    client = NanoBananaClient()
    print(f"✅ Client initialized with model: {client.image_model}")
    
    # Create a simple test image (or use an existing one)
    # For this test, we'll create a simple colored square
    test_image = Image.new('RGB', (512, 512), color='lightblue')
    
    # Save to bytes
    img_bytes = BytesIO()
    test_image.save(img_bytes, format='PNG')
    image_data = img_bytes.getvalue()
    
    print(f"📸 Created test image: {len(image_data)} bytes")
    
    # Test prompt for rhinoplasty
    prompt = """Modify this face to show rhinoplasty results:
- Straighten the nasal bridge
- Refine and slightly elevate the nasal tip
- Maintain natural facial proportions
- Preserve skin texture and tone
- Keep the same lighting and angle"""
    
    try:
        print("🎨 Generating edited image...")
        edited_image_data = await client.edit_image(
            image_data=image_data,
            prompt=prompt
        )
        
        print(f"✅ Successfully generated image: {len(edited_image_data)} bytes")
        
        # Save the result
        output_path = Path(__file__).parent / "test_output_image.png"
        with open(output_path, 'wb') as f:
            f.write(edited_image_data)
        
        print(f"💾 Saved result to: {output_path}")
        
        # Verify it's a valid image
        result_image = Image.open(BytesIO(edited_image_data))
        print(f"🖼️  Result image size: {result_image.size}, mode: {result_image.mode}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_text_generation():
    """Test text generation."""
    print("\n🧪 Testing text generation...")
    
    client = NanoBananaClient()
    
    try:
        result = await client.generate_text(
            prompt="Explain what rhinoplasty is in one sentence.",
            max_tokens=100,
            temperature=0.3
        )
        
        print(f"✅ Generated text: {result['text'][:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Gemini 2.0 Flash + Imagen 3 Test Suite")
    print("=" * 60)
    
    # Test text generation first (simpler)
    text_ok = await test_text_generation()
    
    # Test image generation
    image_ok = await test_image_generation()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"  Text Generation: {'✅ PASS' if text_ok else '❌ FAIL'}")
    print(f"  Image Generation: {'✅ PASS' if image_ok else '❌ FAIL'}")
    print("=" * 60)
    
    return text_ok and image_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
