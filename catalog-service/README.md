# catalog-service

Microservice Django REST dédié au catalogue produit.

## Objectif

Ce service est responsable uniquement de:
- catégories
- produits
- prix
- stock

Aucun autre service ne doit accéder directement à sa base PostgreSQL.

## Stack technique

- Django
- Django REST Framework
- PostgreSQL
- Docker Compose

## Démarrage

Depuis le dossier catalog-service:

```bash
docker compose up --build
```

Port API utilisé: 8000
Port PostgreSQL utilisé: 5432

URL API:

- http://localhost:8000/api/

## Endpoints obligatoires

- GET /api/categories/
- GET /api/products/
- GET /api/products/<id>/

Bonus ajouté:

- GET /api/products/active/ (uniquement les produits actifs)
- Filtrage catégorie: GET /api/products/?category=sneakers
- Recherche nom: GET /api/products/?search=nike
- Filtres aussi disponibles sur /api/products/active/

Endpoint utilitaire:

- GET /api/health/

## Documentation API

- OpenAPI JSON: http://localhost:8000/api/schema/
- Swagger UI: http://localhost:8000/api/docs/swagger/
- ReDoc: http://localhost:8000/api/docs/redoc/

## Format JSON

### GET /api/categories/

```json
[
  {
    "id": 1,
    "name": "Sneakers",
    "slug": "sneakers"
  },
  {
    "id": 2,
    "name": "Vestes",
    "slug": "vestes"
  }
]
```

### GET /api/products/

```json
[
  {
    "id": 1,
    "name": "Nike Air Zoom",
    "slug": "nike-air-zoom",
    "description": "Chaussure de running légère",
    "price": "129.90",
    "stock": 12,
    "category": {
      "id": 1,
      "name": "Sneakers",
      "slug": "sneakers"
    },
    "is_active": true
  }
]
```

### GET /api/products/1/

```json
{
  "id": 1,
  "name": "Nike Air Zoom",
  "slug": "nike-air-zoom",
  "description": "Chaussure de running légère",
  "price": "129.90",
  "stock": 12,
  "category": {
    "id": 1,
    "name": "Sneakers",
    "slug": "sneakers"
  },
  "is_active": true
}
```

## Jeu de données de test

Au démarrage Docker, le service exécute:

1. migrate
2. seed_catalog

Le seed injecte:
- 3 catégories: Sneakers, Vestes, Accessoires
- 8 produits:
  - Nike Air Zoom
  - Adidas Forum Low
  - Puma Rider
  - Veste en jean
  - Doudoune légère
  - Sac sport
  - Casquette noire
  - Chaussettes running

Initialisation manuelle possible:

```bash
docker compose exec catalog-service python manage.py seed_catalog
```
