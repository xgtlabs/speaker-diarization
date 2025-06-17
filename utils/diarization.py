from pyannote.audio import Pipeline
from huggingface_hub import login
import torch
import logging
from .exceptions import DiarizationError

logger = logging.getLogger(__name__)

def diarize_audio(audio_path: str, hf_token: str, min_speakers: int = 1, max_speakers: int = 10) -> list:
    """
    Effectue la diarisation d'un fichier audio
    
    Args:
        audio_path: Chemin vers le fichier audio
        hf_token: Token Hugging Face
        min_speakers: Nombre minimum de locuteurs
        max_speakers: Nombre maximum de locuteurs
    
    Returns:
        Liste des segments avec informations des locuteurs
    
    Raises:
        DiarizationError: En cas d'erreur lors de la diarisation
    """
    try:
        logger.info("Début de la diarisation")
        
        # Connexion à Hugging Face
        login(hf_token)
        
        # Chargement de la pipeline avec gestion des erreurs
        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
        except Exception as e:
            logger.error(f"Erreur de chargement de la pipeline: {e}")
            # Fallback vers une version antérieure
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization@2.1",
                use_auth_token=hf_token
            )
        
        if pipeline is None:
            raise DiarizationError("Impossible de charger la pipeline de diarisation")
        
        # Configuration des paramètres
        if hasattr(pipeline, '_segmentation'):
            pipeline._segmentation.min_speakers = min_speakers
            pipeline._segmentation.max_speakers = max_speakers
        
        logger.info("Exécution de la diarisation...")
        
        # Exécution de la diarisation
        diarization_result = pipeline(audio_path)
        
        # Extraction des segments
        segments = []
        for turn, _, speaker in diarization_result.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": float(turn.start),
                "end": float(turn.end)
            })
        
        logger.info(f"Diarisation terminée: {len(segments)} segments trouvés")
        return segments
        
    except Exception as e:
        logger.error(f"Erreur lors de la diarisation: {e}")
        raise DiarizationError(f"Erreur lors de la diarisation: {str(e)}")

def validate_audio_file(audio_path: str) -> bool:
    """Valide que le fichier audio est accessible et lisible"""
    try:
        import torchaudio
        info = torchaudio.info(audio_path)
        logger.info(f"Fichier audio validé: {info.sample_rate}Hz, {info.num_frames} frames")
        return True
    except Exception as e:
        logger.error(f"Fichier audio invalide: {e}")
        return False
