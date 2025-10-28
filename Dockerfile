# Utiliser Python 3.11 comme image de base
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code source
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p data/raw data/chroma_db

# Exposer le port Streamlit (8501)
EXPOSE 8501

# Healthcheck pour vérifier que l'application fonctionne
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Commande pour lancer l'application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]