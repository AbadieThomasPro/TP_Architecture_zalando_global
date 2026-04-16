# Seed SQL pour 100 000 produits et 50 categories

Ce script est prevu pour PostgreSQL avec les tables Django suivantes :
- catalog_category
- catalog_product

Il complete les donnees existantes pour arriver a :
- 50 categories au total
- 100 001 produits au total
- ids produits de 0 a 100 000

~~~sql
-- DBeaver (Auto-commit ON) : executer tel quel.
-- Si Auto-commit est OFF, vous pouvez entourer le script avec BEGIN; ... COMMIT;.

-- 0) Ecraser les donnees existantes
TRUNCATE TABLE catalog_product, catalog_category RESTART IDENTITY CASCADE;

-- 1) Inserer 50 categories (ids 1 -> 50)
INSERT INTO catalog_category (id, name, slug)
SELECT
    i,
    'Category ' || i,
    'category-' || i
FROM generate_series(1, 50) AS s(i);

-- 2) Inserer les produits (ids 0 -> 100000)
INSERT INTO catalog_product (
    id,
    name,
    slug,
    description,
    price,
    stock,
    is_active,
    category_id
)
SELECT
    i,
    'Product ' || i,
    'product-' || i,
    'Description for product ' || i,
    ROUND((5 + random() * 495)::numeric, 2),
    (random() * 100)::int,
    TRUE,
    (i % 50) + 1
FROM generate_series(1, 100000) AS s(i);

-- 3) Recaler les sequences apres insertion manuelle des ids
SELECT setval(
    pg_get_serial_sequence('catalog_category', 'id'),
    (SELECT MAX(id) FROM catalog_category),
    true
);

SELECT setval(
    pg_get_serial_sequence('catalog_product', 'id'),
    (SELECT MAX(id) FROM catalog_product),
    true
);
~~~

Verification rapide :

~~~sql
SELECT COUNT(*) AS categories_total FROM catalog_category;
SELECT COUNT(*) AS products_total FROM catalog_product;
SELECT MIN(id) AS min_id, MAX(id) AS max_id FROM catalog_product;
~~~


CUSTOMERS

~~~~sql
BEGIN;

TRUNCATE TABLE customers_address, customers_customer RESTART IDENTITY CASCADE;

WITH countries AS (
    SELECT *
    FROM (
        VALUES
            (1, 'France', 'Paris'),
            (2, 'Germany', 'Berlin'),
            (3, 'Spain', 'Madrid'),
            (4, 'Italy', 'Rome'),
            (5, 'Portugal', 'Lisbon'),
            (6, 'Belgium', 'Brussels'),
            (7, 'Netherlands', 'Amsterdam'),
            (8, 'Switzerland', 'Zurich'),
            (9, 'Austria', 'Vienna'),
            (10, 'Poland', 'Warsaw'),
            (11, 'Czech Republic', 'Prague'),
            (12, 'Hungary', 'Budapest'),
            (13, 'Denmark', 'Copenhagen'),
            (14, 'Sweden', 'Stockholm'),
            (15, 'Norway', 'Oslo'),
            (16, 'Finland', 'Helsinki'),
            (17, 'Ireland', 'Dublin'),
            (18, 'United Kingdom', 'London'),
            (19, 'Greece', 'Athens'),
            (20, 'Romania', 'Bucharest'),
            (21, 'Bulgaria', 'Sofia'),
            (22, 'Croatia', 'Zagreb'),
            (23, 'Serbia', 'Belgrade'),
            (24, 'Slovakia', 'Bratislava'),
            (25, 'Slovenia', 'Ljubljana'),
            (26, 'Ukraine', 'Kyiv'),
            (27, 'Morocco', 'Casablanca'),
            (28, 'Algeria', 'Algiers'),
            (29, 'Tunisia', 'Tunis'),
            (30, 'Canada', 'Montreal')
    ) AS t(idx, country, city)
),
inserted_customers AS (
    INSERT INTO customers_customer (first_name, last_name, email, phone, is_active)
    SELECT
        'Customer' || LPAD(gs::text, 5, '0'),
        'Test' || LPAD(gs::text, 5, '0'),
        'customer' || LPAD(gs::text, 5, '0') || '@example.com',
        '06' || LPAD(gs::text, 8, '0'),
        TRUE
    FROM generate_series(1, 10000) AS gs
    RETURNING id
)
INSERT INTO customers_address (customer_id, street, postal_code, city, country, is_default)
SELECT
    ic.id,
    (100 + ic.id) || ' Main Street',
    LPAD((10000 + (ic.id % 90000))::text, 5, '0'),
    c.city,
    c.country,
    TRUE
FROM inserted_customers ic
JOIN countries c
    ON c.idx = ((ic.id - 1) % 30) + 1;

COMMIT;
~~~