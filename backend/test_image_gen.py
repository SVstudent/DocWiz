#!/usr/bin/env python3
"""Test script to debug Gemini image generation."""
import os
import sys
from io import BytesIO

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google import genai
from google.genai import types
from PIL import Image
import base64

# Get API key from environment or .env
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("NANO_BANANA_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: No API key found. Set NANO_BANANA_API_KEY, GOOGLE_API_KEY, or GEMINI_API_KEY")
    sys.exit(1)

print(f"Using API key: {api_key[:10]}...")

# Initialize client
client = genai.Client(api_key=api_key)
print(f"Client initialized: {type(client)}")

# Create a simple test image (solid color)
test_image = Image.new('RGB', (512, 512), color='lightblue')
print(f"Created test image: {test_image.size}, mode: {test_image.mode}")

# Simple prompt for testing
prompt = "Generate a picture of a cute cartoon bunny"

print(f"\n=== Testing text-to-image (no input image) ===")
print(f"Prompt: {prompt}")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["Image", "Text"],
        )
    )
    
    print(f"\nResponse type: {type(response)}")
    print(f"Response attrs: {[a for a in dir(response) if not a.startswith('_')]}")
    
    if hasattr(response, 'candidates') and response.candidates:
        print(f"Found {len(response.candidates)} candidates")
        for i, cand in enumerate(response.candidates):
            print(f"  Candidate {i}:")
            if hasattr(cand, 'finish_reason'):
                print(f"    finish_reason: {cand.finish_reason}")
            if hasattr(cand, 'content') and cand.content:
                print(f"    parts: {len(cand.content.parts)}")
                for j, part in enumerate(cand.content.parts):
                    if hasattr(part, 'text') and part.text:
                        print(f"      Part {j}: TEXT - {part.text[:100]}...")
                    if hasattr(part, 'inline_data') and part.inline_data:
                        print(f"      Part {j}: IMAGE - mime: {part.inline_data.mime_type}")
                        # Try to save
                        if hasattr(part.inline_data, 'data') and part.inline_data.data:
                            with open("test_output_simple.jpg", "wb") as f:
                                f.write(part.inline_data.data)
                            print(f"      Saved to test_output_simple.jpg")
    else:
        print("No candidates in response!")
        
    if hasattr(response, 'text') and response.text:
        print(f"\nResponse text: {response.text}")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== Testing image editing (with input image) ===")
prompt2 = "Create a picture based on this image but add a rainbow in the sky"
print(f"Prompt: {prompt2}")

try:
    response2 = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt2, test_image],
        config=types.GenerateContentConfig(
            response_modalities=["Image", "Text"],
        )
    )
    
    print(f"\nResponse type: {type(response2)}")
    
    if hasattr(response2, 'candidates') and response2.candidates:
        print(f"Found {len(response2.candidates)} candidates")
        for i, cand in enumerate(response2.candidates):
            print(f"  Candidate {i}:")
            if hasattr(cand, 'finish_reason'):
                print(f"    finish_reason: {cand.finish_reason}")
            if hasattr(cand, 'content') and cand.content:
                print(f"    parts: {len(cand.content.parts)}")
                for j, part in enumerate(cand.content.parts):
                    if hasattr(part, 'text') and part.text:
                        print(f"      Part {j}: TEXT - {part.text[:100]}...")
                    if hasattr(part, 'inline_data') and part.inline_data:
                        print(f"      Part {j}: IMAGE - mime: {part.inline_data.mime_type}")
                        if hasattr(part.inline_data, 'data') and part.inline_data.data:
                            with open("test_output_edit.jpg", "wb") as f:
                                f.write(part.inline_data.data)
                            print(f"      Saved to test_output_edit.jpg")
    else:
        print("No candidates in response!")
        
    if hasattr(response2, 'text') and response2.text:
        print(f"\nResponse text: {response2.text}")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Done ===")
