import os
import json
import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


CONFIG = load_config()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_json(prompt: str) -> dict:
    """Send a prompt to Gemini and get back a Python dict (JSON only)."""
    response = _client.models.generate_content(
        model=CONFIG["llm_model"],
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    return json.loads(response.text)