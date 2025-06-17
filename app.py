import streamlit as st
import tempfile
import os
import logging
from pathlib import Path
from utils.diarization import diarize_audio
from utils.summarizer import summarize_with_ollama
from utils.audio_processor import process_audio_file
from utils.exceptions import DiarizationError, SummarizationError

# Configuration de la page
st.set_page_config(
    page_title="Diarisation + Résumé", 
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.title("🧠 Diarisation + Résumé conversationnel")
    st.markdown("---")
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        hf_token = st.text_input(
            "🔑 Token Hugging Face", 
            type="password",
            help="Token nécessaire pour accéder au modèle de diarisation"
        )
        
        # Options avancées
        st.subheader("Options avancées")
        min_speakers = st.number_input("Nombre minimum de locuteurs", min_value=1, max_value=10, value=1)
        max_speakers = st.number_input("Nombre maximum de locuteurs", min_value=1, max_value=10, value=10)
        
        ollama_model = st.selectbox(
            "Modèle Ollama pour le résumé",
            ["llama3", "llama2", "mistral", "codellama"],
            help="Modèle utilisé pour générer le résumé"
        )
        
        # Test de connexion Ollama
        if st.button("🔍 Tester la connexion Ollama"):
            try:
                from utils.summarizer import test_ollama_connection
                if test_ollama_connection():
                    st.success("✅ Ollama est accessible")
                else:
                    st.error("❌ Ollama n'est pas accessible")
            except Exception as e:
                st.error(f"❌ Erreur de connexion : {e}")
    
    # Interface principale
    uploaded_file = st.file_uploader(
        "🎤 Uploadez votre fichier audio", 
        type=["wav", "mp3", "m4a", "flac"],
        help="Formats supportés: WAV, MP3, M4A, FLAC"
    )
    
    if uploaded_file and hf_token:
        # Informations sur le fichier
        file_details = {
            "Nom": uploaded_file.name,
            "Taille": f"{uploaded_file.size / 1024 / 1024:.2f} MB",
            "Type": uploaded_file.type
        }
        
        st.info("📁 **Informations du fichier:**")
        for key, value in file_details.items():
            st.write(f"- **{key}:** {value}")
        
        if st.button("🚀 Démarrer l'analyse", type="primary"):
            process_audio(uploaded_file, hf_token, min_speakers, max_speakers, ollama_model)
    
    elif uploaded_file and not hf_token:
        st.warning("⚠️ Veuillez saisir votre token Hugging Face pour continuer.")
    elif hf_token and not uploaded_file:
        st.info("👆 Uploadez un fichier audio pour commencer l'analyse.")

def process_audio(uploaded_file, hf_token, min_speakers, max_speakers, ollama_model):
    """Traite le fichier audio complet"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Étape 1: Sauvegarde temporaire
        status_text.text("💾 Sauvegarde du fichier...")
        progress_bar.progress(10)
        
        with tempfile.NamedTemporaryFile(suffix=f".{uploaded_file.name.split('.')[-1]}", delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        
        # Étape 2: Traitement audio
        status_text.text("🔊 Traitement du fichier audio...")
        progress_bar.progress(25)
        
        processed_path = process_audio_file(tmp_path)
        
        # Étape 3: Diarisation
        status_text.text("🎯 Diarisation en cours...")
        progress_bar.progress(40)
        
        segments = diarize_audio(
            processed_path, 
            hf_token, 
            min_speakers=min_speakers, 
            max_speakers=max_speakers
        )
        
        progress_bar.progress(70)
        status_text.text("✅ Diarisation terminée!")
        
        # Affichage des résultats
        display_diarization_results(segments)
        
        # Étape 4: Génération du résumé
        if st.button("📝 Générer le résumé"):
            status_text.text("🤖 Génération du résumé...")
            progress_bar.progress(90)
            
            transcript = format_transcript(segments)
            summary = summarize_with_ollama(transcript, ollama_model)
            
            progress_bar.progress(100)
            status_text.text("🎉 Analyse terminée!")
            
            display_summary(summary)
        
    except DiarizationError as e:
        st.error(f"❌ Erreur de diarisation : {e}")
        logger.error(f"Diarization error: {e}")
    except SummarizationError as e:
        st.error(f"❌ Erreur de résumé : {e}")
        logger.error(f"Summarization error: {e}")
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {e}")
        logger.error(f"Unexpected error: {e}")
    finally:
        # Nettoyage des fichiers temporaires
        cleanup_temp_files([tmp_path, processed_path] if 'processed_path' in locals() else [tmp_path])

def display_diarization_results(segments):
    """Affiche les résultats de la diarisation"""
    st.subheader("🎯 Résultats de la diarisation")
    st.success(f"✅ {len(segments)} segments détectés")
    
    # Statistiques
    speakers = set(seg['speaker'] for seg in segments)
    total_duration = max(seg['end'] for seg in segments) if segments else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Locuteurs", len(speakers))
    with col2:
        st.metric("📊 Segments", len(segments))
    with col3:
        st.metric("⏱️ Durée totale", f"{total_duration:.1f}s")
    
    # Affichage détaillé
    with st.expander("📋 Détails des segments", expanded=True):
        for i, seg in enumerate(segments):
            duration = seg['end'] - seg['start']
            st.write(
                f"**Segment {i+1}:** "
                f"[{seg['start']:.2f}s - {seg['end']:.2f}s] "
                f"**{seg['speaker']}** "
                f"({duration:.2f}s)"
            )

def display_summary(summary):
    """Affiche le résumé généré"""
    st.subheader("📝 Résumé de la conversation")
    st.success("✅ Résumé généré avec succès!")
    
    # Affichage du résumé avec styling
    st.markdown("### 📄 Contenu du résumé")
    st.markdown(f"```text\n{summary}\n```")
    
    # Option de téléchargement
    st.download_button(
        label="💾 Télécharger le résumé",
        data=summary,
        file_name="resume_conversation.txt",
        mime="text/plain"
    )

def format_transcript(segments):
    """Formate la transcription pour le résumé"""
    transcript = ""
    for seg in segments:
        duration = seg['end'] - seg['start']
        transcript += f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['speaker']} parle pendant {duration:.1f} secondes.\n"
    return transcript

def cleanup_temp_files(file_paths):
    """Nettoie les fichiers temporaires"""
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.unlink(path)
                logger.info(f"Fichier temporaire supprimé: {path}")
        except Exception as e:
            logger.warning(f"Impossible de supprimer {path}: {e}")

if __name__ == "__main__":
    main()