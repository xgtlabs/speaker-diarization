import requests

def summarize_with_ollama(transcript: str, model: str = "llama3") -> str:
    prompt = f"Voici une transcription d'une conversation multi-intervenants :\n\n{transcript}\n\nFais un résumé clair et concis."
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]
