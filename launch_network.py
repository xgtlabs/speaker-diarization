"""
Script pour lancer l'application en mode réseau local
"""

import subprocess
import socket
import sys
import os
from pathlib import Path

def get_local_ip():
    """Récupère l'adresse IP locale"""
    try:
        # Connexion à une adresse externe pour déterminer l'IP locale
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        try:
            # Méthode alternative
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception:
            return "127.0.0.1"

def check_port_available(host, port):
    """Vérifie si le port est disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
        return True
    except OSError:
        return False

def find_available_port(start_port=8501):
    """Trouve un port disponible"""
    for port in range(start_port, start_port + 10):
        if check_port_available("0.0.0.0", port):
            return port
    raise RuntimeError("Aucun port disponible trouvé")

def launch_streamlit():
    """Lance Streamlit avec configuration réseau"""
    
    print("🚀 Lancement de l'application Diarisation + Résumé")
    print("=" * 50)
    
    # Vérification des prérequis
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ Erreur: app.py non trouvé dans le répertoire courant")
        sys.exit(1)
    
    # Récupération de l'IP locale
    local_ip = get_local_ip()
    
    # Recherche d'un port disponible
    try:
        port = find_available_port()
    except RuntimeError as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    print(f"🌐 IP locale détectée: {local_ip}")
    print(f"🔌 Port utilisé: {port}")
    print()
    
    # URLs d'accès
    print("📱 URLs d'accès:")
    print(f"   • Local:  http://localhost:{port}")
    print(f"   • Réseau: http://{local_ip}:{port}")
    print()
    
    # Instructions pour autres appareils
    print("📋 Pour accéder depuis d'autres appareils:")
    print(f"   1. Connectez-vous au même réseau WiFi")
    print(f"   2. Ouvrez: http://{local_ip}:{port}")
    print()
    
    # Configuration du pare-feu (Windows)
    if os.name == 'nt':
        print("🔥 Note Windows: Si l'accès échoue, autorisez Python dans le pare-feu")
        print("   Paramètres > Réseau > Pare-feu Windows > Autoriser une app")
        print()
    
    # Commande Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.address", "0.0.0.0",
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    print("▶️  Démarrage de Streamlit...")
    print()
    
    try:
        # Lancement de Streamlit
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Application arrêtée par l'utilisateur")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    launch_streamlit()