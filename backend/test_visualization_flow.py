#!/usr/bin/env python3
"""Test the complete visualization flow with gemini-2.5-flash-image."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.nano_banana_client import NanoBananaClient
from PIL import Image
from io import BytesIO


async def test_complete_flow():
    """Test the complete visualization flow."""
    print("=" * 70)
    print("Testing Complete Visualization Flow with gemini-2.5-flash-image")
    print("=" * 70)
    
    # Step 1: Create a test image
    print("\n1️⃣  Creating test image...")
    test_image = Image.new('RGB', (512, 512), color='lightblue')
    img_bytes = BytesIO()
    test_image.save(img_bytes, format='PNG')
    image_data = img_bytes.getvalue()
    print(f"   ✅ Created test image: {len(image_data)} bytes")
    
    # Step 2: Initialize NanoBanana client
    print("\n2️⃣  Initializing NanoBanana client...")
    client = NanoBananaClient()
    print(f"   ✅ Client initialized")
    print(f"   📝 Image model: {client.image_model}")
    print(f"   📝 Text model: {client.text_model}")
    
    # Step 3: Test text generation first (simpler)
    print("\n3️⃣  Testing text generation...")
    try:
        text_result = await client.generate_text(
            prompt="Explain rhinoplasty in one sentence.",
            max_tokens=100,
            temperature=0.3
        )
        print(f"   ✅ Text generation successful")
        print(f"   📝 Generated: {text_result['text'][:100]}...")
    except Exception as e:
        print(f"   ❌ Text generation failed: {e}")
        return False
    
    # Step 4: Test image editing with surgical prompt
    print("\n4️⃣  Testing image editing with gemini-2.5-flash-image...")
    surgical_prompt = """Modify this face to show rhinoplasty results:
- Straighten the nasal bridge
- Refine and slightly elevate the nasal tip
- Maintain natural facial proportions
- Preserve skin texture and tone
- Keep the same lighting and angle"""
    
    try:
        print(f"   📤 Sending request to {client.image_model}...")
        edited_image_data = await client.edit_image(
            image_data=image_data,
            prompt=surgical_prompt
        )
        
        print(f"   ✅ Image editing successful!")
        print(f"   📝 Generated image size: {len(edited_image_data)} bytes")
        
        # Verify it's a valid image
        result_image = Image.open(BytesIO(edited_image_data))
        print(f"   📝 Result image dimensions: {result_image.size}")
        print(f"   📝 Result image mode: {result_image.mode}")
        
        # Save the result
        output_path = Path(__file__).parent / "test_visualization_output.png"
        with open(output_path, 'wb') as f:
            f.write(edited_image_data)
        print(f"   💾 Saved result to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Image editing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    success = await test_complete_flow()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED - Visualization flow is working!")
        print("\nThe gemini-2.5-flash-image model is properly configured and")
        print("will generate actual images when you click visualization.")
    else:
        print("❌ TESTS FAILED - Please check the errors above")
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
