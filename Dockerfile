# 1. Image de base légère Python officielle
FROM python:3.11-slim

# Evite la création de fichiers .pyc et force l'affichage direct des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# 2. Installation des dépendances système requises
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# 4. Copie du code source de l'application
COPY . .

# Copie et attribution des droits d'exécution sur le script d'entrée
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exposer le port interne de FastAPI
EXPOSE 8000

# Le script s'exécute en premier, puis lance la commande transmise dans CMD
ENTRYPOINT ["/entrypoint.sh"]
# 5. Commande de démarrage avec Gunicorn (4 workers uvicorn)
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
