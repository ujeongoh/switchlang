# app/check_models.py
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No API Key found. Please set GEMINI_API_KEY in your .env file.")
else:
    client = genai.Client(api_key=api_key)
    print("📋 Available Models:")
    try:
        for m in client.models.list():
            # print that 'generateContent' feature is supported
            if "generateContent" in m.supported_actions:
                # remove the "models/" prefix from the model name and print it
                model_name = m.name.split("/")[-1]
                print(f"- {model_name}")
    except Exception as e:
        print(f"Error occurred: {e}")