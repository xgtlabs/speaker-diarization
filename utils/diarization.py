from pyannote.audio import Pipeline
from huggingface_hub import login
import torch
import logging
import os
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
        
        # Validation du token
        if not hf_token or hf_token.strip() == "":
            raise DiarizationError("Token Hugging Face manquant ou invalide")
        
        # Validation du fichier audio
        if not validate_audio_file(audio_path):
            raise DiarizationError("Fichier audio invalide ou inaccessible")
        
        # Connexion à Hugging Face avec gestion d'erreur
        try:
            login(token=hf_token)
            logger.info("Connexion à Hugging Face réussie")
        except Exception as e:
            logger.error(f"Erreur de connexion Hugging Face: {e}")
            raise DiarizationError(f"Erreur de connexion Hugging Face: {str(e)}")
        
        # Tentative de chargement de la pipeline principale
        pipeline = None
        model_configs = [
            {
                "name": "pyannote/speaker-diarization-3.1",
                "version": "3.1"
            },
            {
                "name": "pyannote/speaker-diarization",
                "version": "2.1"
            }
        ]
        
        for config in model_configs:
            try:
                logger.info(f"Tentative de chargement du modèle {config['name']}")
                
                # Différentes méthodes selon le modèle
                if config["version"] == "3.1":
                    pipeline = Pipeline.from_pretrained(
                        config["name"],
                        use_auth_token=hf_token
                    )
                else:
                    pipeline = Pipeline.from_pretrained(
                        f"{config['name']}@{config['version']}",
                        use_auth_token=hf_token
                    )
                
                if pipeline is not None:
                    logger.info(f"Pipeline {config['name']} chargée avec succès")
                    break
                    
            except Exception as e:
                logger.warning(f"Échec du chargement de {config['name']}: {e}")
                continue
        
        # Vérification finale
        if pipeline is None:
            raise DiarizationError(
                "Impossible de charger aucune pipeline de diarisation. "
                "Vérifiez votre token Hugging Face et l'accès aux modèles."
            )
        
        # Configuration du device (GPU si disponible)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Utilisation du device: {device}")
        
        # Configuration des paramètres de diarisation
        try:
            # Pour pyannote.audio 3.x
            if hasattr(pipeline, 'instantiate'):
                pipeline = pipeline.instantiate({"min_speakers": min_speakers, "max_speakers": max_speakers})
            # Pour les versions antérieures
            elif hasattr(pipeline, '_segmentation'):
                if hasattr(pipeline._segmentation, 'min_speakers'):
                    pipeline._segmentation.min_speakers = min_speakers
                    pipeline._segmentation.max_speakers = max_speakers
        except Exception as e:
            logger.warning(f"Impossible de configurer les paramètres de locuteurs: {e}")
        
        logger.info(f"Exécution de la diarisation sur {audio_path}...")
        
        # Exécution de la diarisation avec gestion d'erreur
        try:
            diarization_result = pipeline(audio_path)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la pipeline: {e}")
            raise DiarizationError(f"Erreur lors de l'exécution: {str(e)}")
        
        # Vérification du résultat
        if diarization_result is None:
            raise DiarizationError("Résultat de diarisation vide")
        
        # Extraction des segments
        segments = []
        try:
            for turn, _, speaker in diarization_result.itertracks(yield_label=True):
                segments.append({
                    "speaker": speaker,
                    "start": float(turn.start),
                    "end": float(turn.end),
                    "duration": float(turn.end - turn.start)
                })
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des segments: {e}")
            raise DiarizationError(f"Erreur lors de l'extraction: {str(e)}")
        
        # Validation du résultat
        if not segments:
            logger.warning("Aucun segment de diarisation trouvé")
            return [{
                "speaker": "SPEAKER_00",
                "start": 0.0,
                "end": get_audio_duration(audio_path),
                "duration": get_audio_duration(audio_path)
            }]
        
        # Tri des segments par temps de début
        segments.sort(key=lambda x: x["start"])
        
        logger.info(f"Diarisation terminée: {len(segments)} segments trouvés")
        logger.info(f"Locuteurs détectés: {len(set(seg['speaker'] for seg in segments))}")
        
        return segments
        
    except DiarizationError:
        # Re-lever les erreurs de diarisation
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la diarisation: {e}")
        raise DiarizationError(f"Erreur inattendue: {str(e)}")

def validate_audio_file(audio_path: str) -> bool:
    """Valide que le fichier audio est accessible et lisible"""
    try:
        if not os.path.exists(audio_path):
            logger.error(f"Fichier audio non trouvé: {audio_path}")
            return False
            
        import torchaudio
        info = torchaudio.info(audio_path)
        
        if info.num_frames == 0:
            logger.error("Fichier audio vide")
            return False
            
        if info.sample_rate <= 0:
            logger.error("Taux d'échantillonnage invalide")
            return False
            
        logger.info(f"Fichier audio validé: {info.sample_rate}Hz, {info.num_frames} frames, {info.num_channels} canaux")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation du fichier audio: {e}")
        return False

def get_audio_duration(audio_path: str) -> float:
    """Récupère la durée du fichier audio"""
    try:
        import torchaudio
        info = torchaudio.info(audio_path)
        return float(info.num_frames / info.sample_rate)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la durée: {e}")
        return 0.0

def check_model_access(hf_token: str) -> dict:
    """Vérifie l'accès aux modèles de diarisation"""
    models_status = {}
    
    models_to_check = [
        "pyannote/speaker-diarization-3.1",
        "pyannote/speaker-diarization"
    ]
    
    try:
        login(token=hf_token)
        
        for model_name in models_to_check:
            try:
                # Tentative de chargement minimal pour vérifier l'accès
                from huggingface_hub import model_info
                info = model_info(model_name, token=hf_token)
                models_status[model_name] = {
                    "accessible": True,
                    "error": None
                }
            except Exception as e:
                models_status[model_name] = {
                    "accessible": False,
                    "error": str(e)
                }
                
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des modèles: {e}")
        
    return models_status