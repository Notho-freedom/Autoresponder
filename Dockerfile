# Utiliser Python 3.11 slim pour une image légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source
COPY . .

# Créer le dossier data (même si non utilisé avec Firestore)
RUN mkdir -p data

# Exposer le port (Render utilise la variable $PORT)
EXPOSE 8000

# Commande pour démarrer l'application
# Render définit automatiquement la variable PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
