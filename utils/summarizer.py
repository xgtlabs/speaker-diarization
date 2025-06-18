import requests
from requests.exceptions import RequestException
import os

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', DEFAULT_OLLAMA_URL)

def summarize_with_ollama(transcript: str, model: str = "llama3") -> str:
    prompt = f"Voici une transcription d'une conversation multi-intervenants :\n\n{transcript}\n\nFais un résumé clair et concis."
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()["response"]
    except RequestException:
        return "Error: Ollama service unavailable or returned an invalid response."
    except (KeyError, ValueError):  # Catch errors from .json() or missing 'response' key
        return "Error: Ollama service returned an invalid response."
