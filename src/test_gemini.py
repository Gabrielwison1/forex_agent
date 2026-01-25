import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing Key: {api_key[:10]}...")

genai.configure(api_key=api_key)

# Try the stable 1.5 Flash model
model_name = "gemini-1.5-flash"

print(f"Attempting to generate content with '{model_name}'...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, are you online?")
    print("\nSUCCESS! Response:")
    print(response.text)
except Exception as e:
    print(f"\nFATAL ERROR:\n{e}")
    
    # Try fallback alias
    print("\nRetrying with 'gemini-pro'...")
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Hello?")
        print("\nSUCCESS with gemini-pro! Response:")
        print(response.text)
    except Exception as e2:
        print(f"Fallback Failed: {e2}")
