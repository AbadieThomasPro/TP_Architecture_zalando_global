FROM python:3.9

WORKDIR /app

# Copie d'abord les dépendances pour tirer parti du cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copie le reste du projet
COPY . .

# Commande par défaut pour lancer le serveur
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]