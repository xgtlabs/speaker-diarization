import requests
import json
import logging
from typing import Optional
from .exceptions import SummarizationError

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"

def test_ollama_connection() -> bool:
    """Teste la connexion à Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Connexion Ollama échouée: {e}")
        return False

def summarize_with_ollama(transcript: str, model: str = "llama3") -> str:
    """
    Génère un résumé de la transcription via Ollama
    
    Args:
        transcript: La transcription à résumer
        model: Le modèle Ollama à utiliser
    
    Returns:
        Le résumé généré
    
    Raises:
        SummarizationError: En cas d'erreur lors de la génération
    """
    try:
        logger.info(f"Génération du résumé avec le modèle {model}")
        
        # Vérification de la connexion
        if not test_ollama_connection():
            raise SummarizationError("Ollama n'est pas accessible. Vérifiez qu'il est démarré.")
        
        # Construction du prompt amélioré
        prompt = create_summary_prompt(transcript)
        
        # Requête à Ollama
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise SummarizationError(f"Erreur HTTP {response.status_code}: {response.text}")
        
        result = response.json()
        
        if "response" not in result:
            raise SummarizationError("Réponse invalide d'Ollama")
        
        summary = result["response"].strip()
        logger.info("Résumé généré avec succès")
        
        return summary
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête Ollama: {e}")
        raise SummarizationError(f"Erreur de connexion à Ollama: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur lors de la génération du résumé: {e}")
        raise SummarizationError(f"Erreur lors de la génération: {str(e)}")

def create_summary_prompt(transcript: str) -> str:
    """Crée un prompt optimisé pour le résumé"""
    return f"""Tu es un assistant spécialisé dans l'analyse de conversations. 

Voici une transcription d'une conversation avec indication des locuteurs et des moments de prise de parole :

{transcript}

Consignes pour le résumé :
1. Identifie les points clés de la conversation
2. Note les différents locuteurs et leurs contributions principales
3. Résume les décisions prises ou les conclusions
4. Mentionne les sujets abordés par ordre d'importance
5. Sois concis mais complet (maximum 200 mots)

Résumé :"""

def get_available_models() -> list:
    """Récupère la liste des modèles Ollama disponibles"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles: {e}")
        return []