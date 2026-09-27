import os
import json
import time
import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv()


def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


CONFIG = load_config()


def get_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
    return key


_client = genai.Client(api_key=get_api_key())


def ask_json(prompt: str, max_retries: int = 4) -> dict:
    """Send a prompt to Gemini and get back a Python dict (JSON only).
    Retries automatically if Gemini's servers are temporarily busy."""
    for attempt in range(1, max_retries + 1):
        try:
            response = _client.models.generate_content(
                model=CONFIG["llm_model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except errors.ServerError:
            if attempt == max_retries:
                raise
            wait = attempt * 5
            print(f"Gemini is busy (attempt {attempt}/{max_retries}). Retrying in {wait}s...")
            time.sleep(wait)