# 🌐 Configuration Réseau Local

## 🚀 Lancement rapide

### Option 1: Script automatique (Recommandé)

```bash
# Sur Linux/Mac
./launch_network.sh
```

### Option 2: Commande directe

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Option 3: Script Python

```bash
python launch_network.py
```

## 📱 Accès depuis d'autres appareils

1. **Trouvez votre IP locale** (affichée au démarrage)
2. **Connectez vos appareils** au même réseau WiFi
3. **Ouvrez dans le navigateur**: `http://VOTRE_IP:8501`

### Exemple d'URLs d'accès:

- **Ordinateur local**: `http://localhost:8501`
- **Téléphone/Tablette**: `http://192.168.1.100:8501`
- **Autre PC**: `http://192.168.1.100:8501`

## 🔧 Configuration avancée

### Variables d'environnement

```bash
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_PORT="8501"
export STREAMLIT_SERVER_HEADLESS="true"
```

### Fichier de configuration Streamlit

Créez `.streamlit/config.toml`:

```toml
[server]
address = "0.0.0.0"
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 🛡️ Sécurité réseau

### Recommandations

- ✅ Utilisez uniquement sur des réseaux de confiance
- ✅ Désactivez l'application après utilisation
- ✅ Considérez un VPN pour l'accès distant
- ❌ N'exposez pas sur Internet sans sécurisation

### Pare-feu (Windows)

Si l'accès échoue depuis d'autres appareils:

1. Allez dans **Paramètres** > **Réseau et Internet**
2. Cliquez sur **Pare-feu Windows**
3. **Autoriser une application** > **Python**
4. Cochez **Privé** et **Public**

### Pare-feu (Linux)

```bash
# UFW (Ubuntu)
sudo ufw allow 8501

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --add-port=8501/tcp --permanent
sudo firewall-cmd --reload
```

## 🔍 Dépannage réseau

### Problèmes courants

| Problème                                            | Solution                                                    |
| ---------------------------------------------------- | ----------------------------------------------------------- |
| **App non accessible depuis autres appareils** | Vérifiez le pare-feu, utilisez `0.0.0.0` comme address   |
| **Port déjà utilisé**                       | Changez le port:`--server.port 8502`                      |
| **IP introuvable**                             | Utilisez `ipconfig` (Windows) ou `ifconfig` (Linux/Mac) |
| **Connexion lente**                            | Vérifiez la qualité du réseau WiFi                       |

### Commandes de diagnostic

```bash
# Trouver votre IP
# Windows
ipconfig | findstr "IPv4"

# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Tester la connectivité
ping VOTRE_IP

# Vérifier les ports ouverts
netstat -an | grep 8501
```

## 📊 Monitoring réseau

### Surveillance des connexions

Le script `launch_network.py` affiche:

- IP locale détectée
- Port utilisé
- URLs d'accès
- Instructions pour autres appareils

### Logs de connexion

Streamlit affiche automatiquement:

```
Network URL: http://192.168.1.100:8501
External URL: http://192.168.1.100:8501
```

## 🔗 Intégration avec d'autres services

### Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name votre-serveur.local;
  
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker (optionnel)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```
