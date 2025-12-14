#!/usr/bin/env python3
"""Test gemini-2.5-flash-image with both prompt and image."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Configure API
genai.configure(api_key='AIzaSyDjBueY40kW24wbpoeGSeILOkmEAlXSS6c')

# Create test image
test_image = Image.new('RGB', (512, 512), color='lightblue')

# Test prompt - starting with "Create a picture"
prompt = "Create a picture of a person's face after rhinoplasty surgery. The nose should be straighter and more refined. The image should be photorealistic and medically accurate."

# Initialize model
model = genai.GenerativeModel('gemini-2.5-flash-image')

print("=" * 70)
print("TEST 1: Passing BOTH prompt AND image (like template)")
print("=" * 70)
print(f"Prompt: {prompt}")
print(f"Image: {test_image.size} {test_image.mode}")
print("\nSending request...")

# Generate content with BOTH prompt and image (as list)
response = model.generate_content([prompt, test_image])

print("\n--- RESPONSE STRUCTURE ---")
print(f"Response type: {type(response)}")
print(f"Has 'parts': {hasattr(response, 'parts')}")

if hasattr(response, 'parts') and response.parts:
    print(f"Number of parts: {len(response.parts)}")
    for i, part in enumerate(response.parts):
        print(f"\n  Part {i}:")
        print(f"    Has 'text': {hasattr(part, 'text')}")
        print(f"    Has 'inline_data': {hasattr(part, 'inline_data')}")
        
        if hasattr(part, 'text') and part.text:
            print(f"    Text: {part.text[:200]}...")
        
        if hasattr(part, 'inline_data'):
            print(f"    inline_data: {part.inline_data}")
            if part.inline_data:
                print(f"    inline_data has 'data': {hasattr(part.inline_data, 'data')}")
                if hasattr(part.inline_data, 'data') and part.inline_data.data:
                    print(f"    ✅ FOUND IMAGE DATA: {len(part.inline_data.data)} bytes")

print("\n" + "=" * 70)
print("TEST 2: Passing ONLY prompt (no image)")
print("=" * 70)

response2 = model.generate_content(prompt)

print("\n--- RESPONSE STRUCTURE ---")
if hasattr(response2, 'parts') and response2.parts:
    print(f"Number of parts: {len(response2.parts)}")
    for i, part in enumerate(response2.parts):
        print(f"\n  Part {i}:")
        if hasattr(part, 'text') and part.text:
            print(f"    Text: {part.text[:200]}...")
        if hasattr(part, 'inline_data') and part.inline_data:
            if hasattr(part.inline_data, 'data') and part.inline_data.data:
                print(f"    ✅ FOUND IMAGE DATA: {len(part.inline_data.data)} bytes")
