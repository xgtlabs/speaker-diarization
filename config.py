"""Configuration de l'application"""
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

# Créer les dossiers nécessaires
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configuration Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3")

# Configuration Hugging Face
HF_MODELS = {
    "diarization": "pyannote/speaker-diarization-3.1",
    "diarization_fallback": "pyannote/speaker-diarization@2.1"
}

# Configuration audio
AUDIO_CONFIG = {
    "target_sample_rate": 16000,
    "supported_formats": ["wav", "mp3", "m4a", "flac"],
    "max_file_size_mb": 100
}

# Configuration de l'interface
UI_CONFIG = {
    "page_title": "Diarisation + Résumé",
    "page_icon": "🧠",
    "layout": "centered"
}