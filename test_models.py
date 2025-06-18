#!/usr/bin/env python3

import os
from huggingface_hub import login, model_info

# Remplacez par votre token
HF_TOKEN = ""

def test_model_access():
    print("🔍 Test d'accès aux modèles PyAnnote...")
    
    try:
        login(token=HF_TOKEN)
        print("✅ Connexion Hugging Face réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    models = [
        "pyannote/speaker-diarization-3.1",
        "pyannote/speaker-diarization", 
        "pyannote/segmentation-3.0",
        "pyannote/embedding"
    ]
    
    for model_name in models:
        try:
            info = model_info(model_name, token=HF_TOKEN)
            print(f"✅ {model_name} - Accessible")
            if hasattr(info, 'gated') and info.gated:
                print(f"   ⚠️  Modèle avec accès restreint")
        except Exception as e:
            print(f"❌ {model_name} - Erreur: {e}")
            if "gated" in str(e).lower():
                print("   💡 Solution: Acceptez les conditions sur Hugging Face")

if __name__ == "__main__":
    test_model_access()
