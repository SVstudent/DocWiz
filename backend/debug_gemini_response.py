#!/usr/bin/env python3
"""Debug script to inspect Gemini 2.5 Flash Image response structure."""
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

# Test prompt
prompt = "Generate a photorealistic image showing rhinoplasty results with a straighter nose."

# Initialize model
model = genai.GenerativeModel('gemini-2.5-flash-image')

print("Sending request to gemini-2.5-flash-image...")
print(f"Prompt: {prompt}\n")

# Generate content
response = model.generate_content([prompt, test_image])

print("=" * 70)
print("RESPONSE STRUCTURE:")
print("=" * 70)

print(f"\nResponse type: {type(response)}")
print(f"Has 'parts' attribute: {hasattr(response, 'parts')}")
print(f"Has 'candidates' attribute: {hasattr(response, 'candidates')}")

if hasattr(response, 'parts'):
    print(f"\nNumber of parts: {len(response.parts)}")
    for i, part in enumerate(response.parts):
        print(f"\n--- Part {i} ---")
        print(f"Part type: {type(part)}")
        print(f"Has 'text': {hasattr(part, 'text')}")
        print(f"Has 'inline_data': {hasattr(part, 'inline_data')}")
        
        if hasattr(part, 'text') and part.text:
            print(f"Text content: {part.text[:200]}...")
        
        if hasattr(part, 'inline_data'):
            print(f"inline_data value: {part.inline_data}")
            if part.inline_data:
                print(f"inline_data type: {type(part.inline_data)}")
                print(f"inline_data attributes: {dir(part.inline_data)}")

if hasattr(response, 'candidates'):
    print(f"\nNumber of candidates: {len(response.candidates)}")
    for i, candidate in enumerate(response.candidates):
        print(f"\n--- Candidate {i} ---")
        if hasattr(candidate, 'content'):
            print(f"Has content: True")
            if hasattr(candidate.content, 'parts'):
                print(f"Content parts: {len(candidate.content.parts)}")

print("\n" + "=" * 70)
print("RAW RESPONSE:")
print("=" * 70)
print(response)
