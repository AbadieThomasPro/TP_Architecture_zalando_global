# Customer Service — Mini Zalando Microservices

## 📌 Description

Ce projet correspond au microservice **customer-service** du TP *Mini Zalando*.
Il est responsable de la gestion des **clients** et de leurs **adresses de livraison**.

Ce service est totalement indépendant et respecte une architecture **microservices** :

* aucune dépendance directe aux produits ou aux commandes
* base de données dédiée
* API REST exposée avec Django REST Framework

---

## 🛠️ Technologies utilisées

* Python 3.9
* Django
* Django REST Framework
* PostgreSQL
* Docker & Docker Compose

---

## 📁 Structure du projet

```
customer-service/
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── README.md
├── customer_service/
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── customers/
    ├── migrations/
    ├── fixtures/
    │   └── customers_data.json
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

---

## ⚙️ Lancement du projet

### 1. Build et démarrage

```bash
docker compose up --build
```

---

### 2. Appliquer les migrations

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

---

### 3. Charger les données de test

```bash
docker compose exec web python manage.py loaddata customers/fixtures/customers_data.json
```

---

### 4. Accéder à l’API

```
http://localhost:8000/api/
```

---

## 🗄️ Modèle de données

### Customer

* id
* first_name
* last_name
* email
* phone
* is_active

### Address

* id
* customer (clé étrangère)
* street
* postal_code
* city
* country
* is_default

---

## 🔗 API REST

### 📍 Endpoints obligatoires

#### 🔹 Récupérer tous les clients

```
GET /api/customers/
```

#### 🔹 Récupérer le détail d’un client

```
GET /api/customers/<id>/
```

#### 🔹 Récupérer les adresses d’un client

```
GET /api/customers/<id>/addresses/
```

---

## 📦 Format des réponses JSON

### Exemple — Liste des clients

```json
[
  {
    "id": 1,
    "first_name": "Sarah",
    "last_name": "Benali",
    "email": "sarah.benali@example.com",
    "phone": "0600000001",
    "is_active": true
  }
]
```

---

### Exemple — Détail d’un client

```json
{
  "id": 1,
  "first_name": "Sarah",
  "last_name": "Benali",
  "email": "sarah.benali@example.com",
  "phone": "0600000001",
  "is_active": true
}
```

---

### Exemple — Adresses d’un client

```json
[
  {
    "id": 1,
    "street": "12 rue des Lilas",
    "postal_code": "38000",
    "city": "Grenoble",
    "country": "France",
    "is_default": true
  }
]
```

---

## ⭐ Bonus implémentés

### ➕ Création d’un client

```
POST /api/customers/
```

Exemple :

```json
{
  "first_name": "Shiny",
  "last_name": "Test",
  "email": "shiny@test.com",
  "phone": "0600009999",
  "is_active": true
}
```

---

### ➕ Création d’une adresse

```
POST /api/addresses/
```

Exemple :

```json
{
  "customer": 1,
  "street": "12 rue des Lilas",
  "postal_code": "38000",
  "city": "Grenoble",
  "country": "France",
  "is_default": true
}
```

---

### 🔍 Recherche d’un client par email

```
GET /api/customers/?email=sarah.benali@example.com
```

---

## 🧪 Données de test

Le projet contient :

* 5 clients minimum
* au moins 1 adresse par client
* au moins 2 clients avec plusieurs adresses

Les données sont fournies dans :

```
customers/fixtures/customers_data.json
```

---

## 🗃️ Base de données

Le service utilise **PostgreSQL** via Docker.

Configuration (settings.py) :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'customer_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}
```

---

## 🐳 Docker

### docker-compose.yml

* service `web` : application Django
* service `db` : PostgreSQL
* volume persistant pour la base de données

---

## ✅ Critères respectés

* Projet Django autonome
* API REST avec Django REST Framework
* Base de données PostgreSQL dédiée
* Isolation du microservice
* Endpoints conformes
* Données de test présentes
* Lancement via Docker Compose

---

## 🚀 Améliorations possibles

* Authentification (JWT)
* Pagination des résultats
* Validation avancée (email unique)
* Documentation API (Swagger / OpenAPI)

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre du TP Microservices — Mini Zalando.
