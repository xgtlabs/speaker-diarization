#!/bin/bash

echo "🚀 Lancement de l'application Diarisation + Résumé"
echo "=================================================="
echo

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

# Vérification de Streamlit
if ! python3 -m streamlit --version &> /dev/null; then
    echo "❌ Streamlit n'est pas installé"
    echo "Installez avec: pip3 install streamlit"
    exit 1
fi

# Rendre le script exécutable
chmod +x "$0"

# Lancement du script Python
python3 launch_network.py