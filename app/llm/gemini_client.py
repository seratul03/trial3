import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_API_URL")

def ask_gemini(prompt: str) -> str:
    # 1. Check if Key exists
    if not GEMINI_API_KEY:
        return "Configuration Error: GEMINI_API_KEY is missing."

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "safety_settings": [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 2. Make the request ONCE (No retry loop)
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )

        # 3. If it failed (400, 429, 500, etc.), return the RAW text from Google
        if response.status_code != 200:
            return f"GOOGLE API ERROR ({response.status_code}): {response.text}"

        # 4. Parse success response
        data = response.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"UNEXPECTED RESPONSE FORMAT: {data}"

    except Exception as e:
        # 5. Catch connection errors (DNS, Timeout, etc.) and show raw error
        return f"PYTHON EXCEPTION: {str(e)}"