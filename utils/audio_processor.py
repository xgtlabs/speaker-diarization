import torch
import torchaudio
import tempfile
import logging
import os
from pathlib import Path
from .exceptions import AudioProcessingError

logger = logging.getLogger(__name__)

def process_audio_file(input_path: str) -> str:
    """
    Traite et normalise un fichier audio pour la diarisation
    
    Args:
        input_path: Chemin vers le fichier audio d'entrée
    
    Returns:
        Chemin vers le fichier audio traité
    
    Raises:
        AudioProcessingError: En cas d'erreur de traitement
    """
    try:
        logger.info(f"Traitement du fichier audio: {input_path}")
        
        # Vérification de l'existence du fichier
        if not os.path.exists(input_path):
            raise AudioProcessingError(f"Fichier non trouvé: {input_path}")
        
        # Chargement du fichier audio avec gestion d'erreur
        try:
            waveform, sample_rate = torchaudio.load(input_path)
        except Exception as e:
            logger.error(f"Erreur lors du chargement audio: {e}")
            raise AudioProcessingError(f"Impossible de charger le fichier audio: {str(e)}")
        
        # Vérification des données audio
        if waveform.numel() == 0:
            raise AudioProcessingError("Fichier audio vide")
        
        logger.info(f"Audio chargé: {waveform.shape}, {sample_rate}Hz")
        
        # Conversion en mono si nécessaire
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
            logger.info("Conversion en mono effectuée")
        
        # Rééchantillonnage à 16kHz si nécessaire
        target_sample_rate = 16000
        if sample_rate != target_sample_rate:
            try:
                resampler = torchaudio.transforms.Resample(sample_rate, target_sample_rate)
                waveform = resampler(waveform)
                sample_rate = target_sample_rate
                logger.info(f"Rééchantillonnage à {target_sample_rate}Hz effectué")
            except Exception as e:
                logger.error(f"Erreur lors du rééchantillonnage: {e}")
                raise AudioProcessingError(f"Erreur de rééchantillonnage: {str(e)}")
        
        # Normalisation du volume
        try:
            waveform = normalize_audio(waveform)
            logger.info("Normalisation audio effectuée")
        except Exception as e:
            logger.warning(f"Erreur lors de la normalisation: {e}")
            # Continuer sans normalisation si erreur
        
        # Sauvegarde du fichier traité
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
            
            torchaudio.save(output_path, waveform, sample_rate)
            logger.info(f"Fichier audio traité sauvegardé: {output_path}")
            
            # Vérification du fichier de sortie
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise AudioProcessingError("Fichier de sortie invalide")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise AudioProcessingError(f"Erreur de sauvegarde: {str(e)}")
        
    except AudioProcessingError:
        # Re-lever les erreurs de traitement audio
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors du traitement audio: {e}")
        raise AudioProcessingError(f"Erreur inattendue: {str(e)}")

def normalize_audio(waveform):
    """Normalise le volume audio"""
    try:
        # Vérification des données d'entrée
        if waveform.numel() == 0:
            return waveform
        
        # Normalisation par la valeur absolue maximale
        max_val = torch.max(torch.abs(waveform))
        
        if max_val > 0:
            # Évite la saturation en limitant à 90% du maximum
            normalized = waveform / max_val * 0.9
            return normalized
        else:
            logger.warning("Signal audio silencieux détecté")
            return waveform
            
    except Exception as e:
        logger.error(f"Erreur lors de la normalisation: {e}")
        return waveform  # Retourne le signal original en cas d'erreur

def get_audio_info(audio_path: str) -> dict:
    """Récupère les informations d'un fichier audio"""
    try:
        if not os.path.exists(audio_path):
            return {"error": "Fichier non trouvé"}
        
        info = torchaudio.info(audio_path)
        
        audio_info = {
            "sample_rate": info.sample_rate,
            "num_frames": info.num_frames,
            "duration": info.num_frames / info.sample_rate if info.sample_rate > 0 else 0,
            "num_channels": info.num_channels,
            "file_size": os.path.getsize(audio_path),
            "format": os.path.splitext(audio_path)[1].lower()
        }
        
        logger.info(f"Informations audio: {audio_info}")
        return audio_info
        
    except Exception as e:
        logger.error(f"Erreur lors de la lecture des informations audio: {e}")
        return {"error": str(e)}

def validate_audio_format(file_path: str) -> bool:
    """Valide le format du fichier audio"""
    try:
        supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in supported_formats:
            logger.error(f"Format non supporté: {file_extension}")
            return False
        
        # Tentative de lecture pour validation
        info = torchaudio.info(file_path)
        
        if info.num_frames <= 0:
            logger.error("Fichier audio vide ou corrompu")
            return False
        
        if info.sample_rate <= 0:
            logger.error("Taux d'échantillonnage invalide")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Fichier audio invalide: {e}")
        return False

def cleanup_audio_file(file_path: str) -> bool:
    """Nettoie un fichier audio temporaire"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Fichier temporaire supprimé: {file_path}")
            return True
        return False
    except Exception as e:
        logger.warning(f"Impossible de supprimer {file_path}: {e}")
        return False