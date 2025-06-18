# Conversation Diarization and Summarization Tool

This project is a Streamlit web application that performs speaker diarization on an audio file and then generates a summary of the conversation using Ollama.

## Features

- Upload audio files (WAV, MP3).
- Speaker diarization to identify different speakers and their speech segments.
- Conversation summarization using a local Ollama instance.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ensure Ollama is running locally:**
    This application uses a local Ollama instance to generate summaries. Make sure you have Ollama installed and running. You can download it from [https://ollama.com/](https://ollama.com/).

## Configuration

-   **Ollama API URL (Optional):**
    By default, the application connects to Ollama at `http://localhost:11434/api/generate`.
    You can customize this by setting the `OLLAMA_API_URL` environment variable. For example:
    ```bash
    export OLLAMA_API_URL="http://my-custom-ollama-host:12345/api/generate"
    ```
    Make sure the URL points to the `/api/generate` endpoint of your Ollama instance.

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Open your web browser:**
    Streamlit will usually open the app automatically in your browser or provide a local URL (e.g., `http://localhost:8501`).

3.  **Using the App:**
    - Enter your Hugging Face User Access Token. This is required to download and use the speaker diarization model from Hugging Face. You can find your token in your Hugging Face account settings.
    - Upload an audio file (supports `.wav` and `.mp3`).
    - The diarization process will start automatically and display the spoken segments.
    - Once diarization is complete, click the "Générer un résumé via Ollama" button to get a summary of the conversation.
