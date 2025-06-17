import torch  # Doit être absolument en première position
import torchaudio
import tempfile
import logging
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
        
        # Chargement du fichier audio
        waveform, sample_rate = torchaudio.load(input_path)
        
        # Conversion en mono si nécessaire
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
            logger.info("Conversion en mono effectuée")
        
        # Rééchantillonnage à 16kHz si nécessaire
        target_sample_rate = 16000
        if sample_rate != target_sample_rate:
            resampler = torchaudio.transforms.Resample(sample_rate, target_sample_rate)
            waveform = resampler(waveform)
            sample_rate = target_sample_rate
            logger.info(f"Rééchantillonnage à {target_sample_rate}Hz effectué")
        
        # Normalisation du volume
        waveform = normalize_audio(waveform)
        
        # Sauvegarde du fichier traité
        output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        torchaudio.save(output_path, waveform, sample_rate)
        
        logger.info(f"Fichier audio traité sauvegardé: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement audio: {e}")
        raise AudioProcessingError(f"Erreur de traitement audio: {str(e)}")

def normalize_audio(waveform):
    """Normalise le volume audio"""
    # Normalisation par la valeur absolue maximale
    max_val = torch.max(torch.abs(waveform))
    if max_val > 0:
        waveform = waveform / max_val * 0.9  # Évite la saturation
    return waveform

def get_audio_info(audio_path: str) -> dict:
    """Récupère les informations d'un fichier audio"""
    try:
        info = torchaudio.info(audio_path)
        return {
            "sample_rate": info.sample_rate,
            "num_frames": info.num_frames,
            "duration": info.num_frames / info.sample_rate,
            "num_channels": info.num_channels
        }
    except Exception as e:
        logger.error(f"Erreur lors de la lecture des informations audio: {e}")
        return {}