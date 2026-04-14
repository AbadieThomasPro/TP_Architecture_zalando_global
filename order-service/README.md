# Order Service — Mini Zalando

Microservice Django / Django REST Framework dédié à la gestion des commandes dans le TP Microservices « Mini Zalando ».

## Objectif

Ce service est responsable de :

- l'enregistrement des commandes ;
- l'enregistrement des lignes de commande ;
- le calcul du montant total ;
- l'exposition d'une API REST pour consulter et créer des commandes.

Dans cette première phase, le service fonctionne de manière autonome avec des données mockées pour les produits et les clients. Il est déjà structuré pour être connecté plus tard à `catalog-service` et `customer-service`.

## Stack technique

- Python 3
- Django 4.2
- Django REST Framework
- PostgreSQL
- Docker / Docker Compose

## Structure du projet

- `config/` : configuration Django
- `orders/` : logique métier du microservice
- `docker-compose.yml` : orchestration du service Django et de PostgreSQL
- `Dockerfile` : image du service
- `.env` : variables d'environnement locales

## Modèle de données

### Order

- `id`
- `customer_id`
- `status`
- `total_amount`
- `created_at`

### OrderLine

- `id`
- `order`
- `product_id`
- `product_name`
- `unit_price`
- `quantity`
- `line_total`

## Lancement du projet

1. Se placer dans le dossier du projet :

```bash
docker compose up --build
```

2. Le service est ensuite disponible sur :

- API : `http://localhost:8003/api/orders/`
- Admin Django : `http://localhost:8003/admin/`

3. La base PostgreSQL est accessible avec :

- host : `localhost`
- port : `5435`
- database : `order_service_db`
- user : `order_service_user`
- password : `order_service_password`

## Endpoints disponibles

### Lister les commandes

```http
GET /api/orders/
```

### Consulter le détail d'une commande

```http
GET /api/orders/<id>/
```

### Créer une commande

```http
POST /api/orders/
Content-Type: application/json
```

Exemple de payload :

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```

Exemple de réponse :

```json
{
  "id": 1,
  "customer_id": 1,
  "status": "confirmed",
  "total_amount": "299.70",
  "created_at": "2026-04-14T12:23:10.784781Z",
  "items": [
    {
      "product_id": 1,
      "product_name": "Nike Air Zoom",
      "unit_price": "129.90",
      "quantity": 2,
      "line_total": "259.80"
    },
    {
      "product_id": 3,
      "product_name": "Puma Rider",
      "unit_price": "39.90",
      "quantity": 1,
      "line_total": "39.90"
    }
  ]
}
```

## Cas testés

Les cas suivants ont été validés :

- création d'une commande valide ;
- récupération de la liste des commandes ;
- validation d'un client inexistant ;
- validation d'un produit inexistant ;
- validation d'une quantité invalide.

## Hypothèses d'intégration

Pour cette phase individuelle :

- les clients sont simulés localement ;
- les produits sont simulés localement ;
- les prix sont récupérés depuis des données mockées ;
- le code est déjà organisé pour permettre plus tard les appels HTTP vers `customer-service` et `catalog-service`.

## Remarques

- Le service ne fournit pas de page d'accueil sur `/`, ce qui explique la `404` sur `http://localhost:8003/`.
- Les routes utiles commencent à `/api/orders/`.
- Le frontend React n'est pas nécessaire pour cette phase individuelle ; il est demandé dans la phase finale d'intégration en trinôme.
