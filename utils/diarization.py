from pyannote.audio import Pipeline
from huggingface_hub import login
import os

def diarize(audio_path: str, hf_token: str):
    try:
        login(hf_token)
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token=hf_token)
        if pipeline is None:
            raise RuntimeError("Échec du chargement de la pipeline. Le token Hugging Face a-t-il accès au modèle ?")

        diarization_result = pipeline(audio_path)
        
        segments = []
        for turn, _, speaker in diarization_result.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })
        return segments

    except Exception as e:
        raise RuntimeError(f"Erreur lors de la diarisation : {e}")
