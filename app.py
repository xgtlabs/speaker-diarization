import streamlit as st
import torchaudio
import tempfile
from utils.diarization import diarize
from utils.summarizer import summarize_with_ollama

st.set_page_config(page_title="Diarisation + Résumé", layout="centered")

st.title("🧠 Diarisation + Résumé conversationnel")
hf_token = st.text_input("🔑 Token Hugging Face (privé)", type="password")

uploaded_file = st.file_uploader("🎤 Upload un fichier audio (wav, mp3)", type=["wav", "mp3"])

if uploaded_file and hf_token:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.info("⏳ Diarisation en cours...")
    segments = diarize(tmp_path, hf_token)

    transcript = ""
    for seg in segments:
        text = f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['speaker']} parle...\n"
        transcript += text
        st.text(text)

    ollama_model = st.text_input("🤖 Modèle Ollama pour le résumé", value="llama3")

    if st.button("📄 Générer un résumé via Ollama"):
        summary = summarize_with_ollama(transcript, model=ollama_model)
        st.subheader("📝 Résumé de la conversation")
        if summary.startswith("Error:"):
            st.error(summary)
        else:
            st.success(summary)
