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




WITH first_names AS (
    SELECT ARRAY[
        'Emma','Lina','Chloe','Lea','Jade','Manon','Camille','Sarah','Ines','Louise',
        'Lucas','Hugo','Louis','Gabriel','Arthur','Jules','Adam','Leo','Nathan','Ethan',
        'Sofia','Maya','Nora','Yasmine','Aya','Alice','Eva','Mila','Louna','Zoe',
        'Noah','Mohamed','Yanis','Amir','Ilyes','Rayan','Nassim','Sami','Imran','Bilal',
        'Anna','Mia','Elena','Julia','Clara','Elisa','Nina','Olivia','Victoria','Lucie'
    ] AS arr
),
last_names AS (
    SELECT ARRAY[
        'Martin','Bernard','Dubois','Thomas','Robert','Richard','Petit','Durand','Leroy','Moreau',
        'Simon','Laurent','Lefebvre','Michel','Garcia','David','Bertrand','Roux','Vincent','Fournier',
        'Morel','Girard','Andre','Lefevre','Mercier','Dupont','Lambert','Bonnet','Francois','Martinez',
        'Legrand','Garnier','Faure','Rousseau','Blanc','Guerin','Muller','Henry','Roussel','Nicolas',
        'Perrin','Morin','Mathieu','Clement','Gauthier','Dumont','Lopez','Fontaine','Chevalier','Robin'
    ] AS arr
),
generated AS (
    SELECT
        c.id,
        fn.arr[((c.id - 1) % array_length(fn.arr, 1)) + 1] AS first_name,
        ln.arr[((c.id * 7 - 1) % array_length(ln.arr, 1)) + 1] AS last_name
    FROM customers_customer c
    CROSS JOIN first_names fn
    CROSS JOIN last_names ln
)
UPDATE customers_customer c
SET
    first_name = g.first_name,
    last_name = g.last_name,
    email = lower(g.first_name || '.' || g.last_name || c.id || '@example.com')
FROM generated g
WHERE c.id = g.id;


-------

BEGIN;

TRUNCATE TABLE catalog_product, catalog_category RESTART IDENTITY CASCADE;

INSERT INTO catalog_category (name, slug) VALUES
('Sneakers', 'sneakers'),
('Running', 'running'),
('Chaussures de ville', 'chaussures-ville'),
('Bottines', 'bottines'),
('Sandales', 'sandales'),
('Escarpins', 'escarpins'),
('Mocassins', 'mocassins'),
('Vestes', 'vestes'),
('Manteaux', 'manteaux'),
('Doudounes', 'doudounes'),
('Blazers', 'blazers'),
('T-shirts', 't-shirts'),
('Polos', 'polos'),
('Chemises', 'chemises'),
('Pulls', 'pulls'),
('Sweats', 'sweats'),
('Jeans', 'jeans'),
('Pantalons', 'pantalons'),
('Chinos', 'chinos'),
('Shorts', 'shorts'),
('Jupes', 'jupes'),
('Robes', 'robes'),
('Combinaisons', 'combinaisons'),
('Leggings', 'leggings'),
('Sacs a main', 'sacs-a-main'),
('Sacs a dos', 'sacs-a-dos'),
('Sacs de voyage', 'sacs-de-voyage'),
('Portefeuilles', 'portefeuilles'),
('Ceintures', 'ceintures'),
('Casquettes', 'casquettes'),
('Bonnets', 'bonnets'),
('Echarpes', 'echarpes'),
('Lunettes de soleil', 'lunettes-soleil'),
('Montres', 'montres'),
('Bijoux', 'bijoux'),
('Chaussettes', 'chaussettes'),
('Sous-vetements', 'sous-vetements'),
('Pyjamas', 'pyjamas'),
('Maillots de bain', 'maillots-de-bain'),
('Tenues de sport', 'tenues-sport'),
('Brassieres de sport', 'brassieres-sport'),
('Chaussures de randonnee', 'chaussures-randonnee'),
('Yoga', 'yoga'),
('Accessoires tech', 'accessoires-tech'),
('Coques et housses', 'coques-housses'),
('Parfums', 'parfums'),
('Soins visage', 'soins-visage'),
('Soins cheveux', 'soins-cheveux'),
('Coffrets cadeaux', 'coffrets-cadeaux'),
('Luxe', 'luxe');

WITH brands AS (
    SELECT ARRAY[
        'Nike','Adidas','Puma','New Balance','Asics','Reebok','Tommy Hilfiger','Calvin Klein',
        'Levi''s','Mango','Zara','Vero Moda','Only','Selected','Jack & Jones','The North Face',
        'Columbia','Lacoste','BOSS','Armani'
    ] AS arr
),
colors AS (
    SELECT ARRAY[
        'Noir','Blanc','Beige','Camel','Marine','Gris','Bordeaux','Kaki','Bleu','Rose',
        'Vert','Ecru','Argent','Dore','Marron'
    ] AS arr
),
materials AS (
    SELECT ARRAY[
        'Coton','Cuir','Denim','Laine','Maille','Satin','Lin','Suede','Toile','Jersey'
    ] AS arr
),
fits AS (
    SELECT ARRAY[
        'Regular','Slim','Oversize','Straight','Relaxed','Classic','Premium','Essential'
    ] AS arr
),
insert_products AS (
    INSERT INTO catalog_product (name, slug, description, price, stock, category_id, is_active)
    SELECT
        CASE c.slug
            WHEN 'sneakers' THEN b || ' Sneaker ' || f || ' ' || col
            WHEN 'running' THEN b || ' Running ' || f || ' ' || col
            WHEN 'chaussures-ville' THEN b || ' Derbies ' || mat || ' ' || col
            WHEN 'bottines' THEN b || ' Bottines ' || f || ' ' || col
            WHEN 'sandales' THEN b || ' Sandales ' || f || ' ' || col
            WHEN 'escarpins' THEN b || ' Escarpins ' || f || ' ' || col
            WHEN 'mocassins' THEN b || ' Mocassins ' || mat || ' ' || col
            WHEN 'vestes' THEN b || ' Veste ' || mat || ' ' || col
            WHEN 'manteaux' THEN b || ' Manteau ' || f || ' ' || col
            WHEN 'doudounes' THEN b || ' Doudoune ' || f || ' ' || col
            WHEN 'blazers' THEN b || ' Blazer ' || f || ' ' || col
            WHEN 't-shirts' THEN b || ' T-shirt ' || f || ' ' || col
            WHEN 'polos' THEN b || ' Polo ' || mat || ' ' || col
            WHEN 'chemises' THEN b || ' Chemise ' || f || ' ' || col
            WHEN 'pulls' THEN b || ' Pull ' || mat || ' ' || col
            WHEN 'sweats' THEN b || ' Sweat ' || f || ' ' || col
            WHEN 'jeans' THEN b || ' Jean ' || f || ' ' || col
            WHEN 'pantalons' THEN b || ' Pantalon ' || f || ' ' || col
            WHEN 'chinos' THEN b || ' Chino ' || f || ' ' || col
            WHEN 'shorts' THEN b || ' Short ' || mat || ' ' || col
            WHEN 'jupes' THEN b || ' Jupe ' || f || ' ' || col
            WHEN 'robes' THEN b || ' Robe ' || f || ' ' || col
            WHEN 'combinaisons' THEN b || ' Combinaison ' || f || ' ' || col
            WHEN 'leggings' THEN b || ' Legging ' || f || ' ' || col
            WHEN 'sacs-a-main' THEN b || ' Sac a main ' || f || ' ' || col
            WHEN 'sacs-a-dos' THEN b || ' Sac a dos ' || f || ' ' || col
            WHEN 'sacs-de-voyage' THEN b || ' Sac de voyage ' || f || ' ' || col
            WHEN 'portefeuilles' THEN b || ' Portefeuille ' || mat || ' ' || col
            WHEN 'ceintures' THEN b || ' Ceinture ' || mat || ' ' || col
            WHEN 'casquettes' THEN b || ' Casquette ' || f || ' ' || col
            WHEN 'bonnets' THEN b || ' Bonnet ' || mat || ' ' || col
            WHEN 'echarpes' THEN b || ' Echarpe ' || mat || ' ' || col
            WHEN 'lunettes-soleil' THEN b || ' Lunettes ' || f || ' ' || col
            WHEN 'montres' THEN b || ' Montre ' || f || ' ' || col
            WHEN 'bijoux' THEN b || ' Bijou ' || f || ' ' || col
            WHEN 'chaussettes' THEN b || ' Chaussettes ' || f || ' ' || col
            WHEN 'sous-vetements' THEN b || ' Sous-vetement ' || f || ' ' || col
            WHEN 'pyjamas' THEN b || ' Pyjama ' || mat || ' ' || col
            WHEN 'maillots-de-bain' THEN b || ' Maillot de bain ' || f || ' ' || col
            WHEN 'tenues-sport' THEN b || ' Tenue de sport ' || f || ' ' || col
            WHEN 'brassieres-sport' THEN b || ' Brassiere sport ' || f || ' ' || col
            WHEN 'chaussures-randonnee' THEN b || ' Randonnee ' || f || ' ' || col
            WHEN 'yoga' THEN b || ' Yoga ' || f || ' ' || col
            WHEN 'accessoires-tech' THEN b || ' Accessoire tech ' || f || ' ' || col
            WHEN 'coques-housses' THEN b || ' Housse ' || f || ' ' || col
            WHEN 'parfums' THEN b || ' Parfum ' || f || ' ' || col
            WHEN 'soins-visage' THEN b || ' Soin visage ' || f || ' ' || col
            WHEN 'soins-cheveux' THEN b || ' Soin cheveux ' || f || ' ' || col
            WHEN 'coffrets-cadeaux' THEN b || ' Coffret ' || f || ' ' || col
            WHEN 'luxe' THEN b || ' Edition Luxe ' || f || ' ' || col
        END || ' ' || gs AS name,

        c.slug || '-' || gs AS slug,

        CASE c.slug
            WHEN 'sneakers' THEN 'Sneaker lifestyle confortable avec amorti et silhouette moderne.'
            WHEN 'running' THEN 'Modele running leger concu pour entrainement regulier.'
            WHEN 'chaussures-ville' THEN 'Chaussure habillee pour bureau et occasions formelles.'
            WHEN 'bottines' THEN 'Bottines polyvalentes avec finition soignee.'
            WHEN 'sandales' THEN 'Sandales legeres ideales pour les beaux jours.'
            WHEN 'escarpins' THEN 'Escarpins elegants a porter en journee ou en soiree.'
            WHEN 'mocassins' THEN 'Mocassins confortables au style chic decontracte.'
            WHEN 'vestes' THEN 'Veste de mi-saison facile a assortir au quotidien.'
            WHEN 'manteaux' THEN 'Manteau structure offrant chaleur et elegance.'
            WHEN 'doudounes' THEN 'Doudoune chaude et pratique pour la saison froide.'
            WHEN 'blazers' THEN 'Blazer moderne au tomber net et polyvalent.'
            WHEN 't-shirts' THEN 'T-shirt en matiere douce pour usage quotidien.'
            WHEN 'polos' THEN 'Polo soigne entre style casual et tenue habillee.'
            WHEN 'chemises' THEN 'Chemise polyvalente a la coupe actuelle.'
            WHEN 'pulls' THEN 'Pull confortable en maille douce.'
            WHEN 'sweats' THEN 'Sweat casual avec coupe confortable.'
            WHEN 'jeans' THEN 'Jean durable en denim avec coupe actuelle.'
            WHEN 'pantalons' THEN 'Pantalon facile a porter en semaine comme le week-end.'
            WHEN 'chinos' THEN 'Chino leger pour un look smart casual.'
            WHEN 'shorts' THEN 'Short confortable pour la saison estivale.'
            WHEN 'jupes' THEN 'Jupe feminine au tomber fluide.'
            WHEN 'robes' THEN 'Robe facile a porter avec une silhouette elegante.'
            WHEN 'combinaisons' THEN 'Combinaison pratique et moderne.'
            WHEN 'leggings' THEN 'Legging extensible offrant confort et maintien.'
            WHEN 'sacs-a-main' THEN 'Sac a main pratique au design urbain.'
            WHEN 'sacs-a-dos' THEN 'Sac a dos fonctionnel avec rangements utiles.'
            WHEN 'sacs-de-voyage' THEN 'Sac de voyage robuste pour week-end et deplacements.'
            WHEN 'portefeuilles' THEN 'Portefeuille compact avec compartiments essentiels.'
            WHEN 'ceintures' THEN 'Ceinture sobre avec boucle metal.'
            WHEN 'casquettes' THEN 'Casquette ajustable au style minimal.'
            WHEN 'bonnets' THEN 'Bonnet doux et chaud pour l hiver.'
            WHEN 'echarpes' THEN 'Echarpe confortable avec toucher agreable.'
            WHEN 'lunettes-soleil' THEN 'Lunettes de soleil au design tendance.'
            WHEN 'montres' THEN 'Montre elegante avec finition soignee.'
            WHEN 'bijoux' THEN 'Bijou raffine pour completer une tenue.'
            WHEN 'chaussettes' THEN 'Chaussettes confortables pour usage quotidien.'
            WHEN 'sous-vetements' THEN 'Sous-vetement doux et confortable.'
            WHEN 'pyjamas' THEN 'Pyjama agreable a porter pour la nuit.'
            WHEN 'maillots-de-bain' THEN 'Maillot de bain pense pour confort et maintien.'
            WHEN 'tenues-sport' THEN 'Tenue de sport respirante pour activites regulieres.'
            WHEN 'brassieres-sport' THEN 'Brassiere sport offrant maintien et confort.'
            WHEN 'chaussures-randonnee' THEN 'Chaussure de randonnee stable avec bonne accroche.'
            WHEN 'yoga' THEN 'Article adapte au yoga et aux pratiques douces.'
            WHEN 'accessoires-tech' THEN 'Accessoire tech pratique pour un usage mobile.'
            WHEN 'coques-housses' THEN 'Protection legere et fonctionnelle pour accessoires.'
            WHEN 'parfums' THEN 'Parfum aux notes equilibrées et modernes.'
            WHEN 'soins-visage' THEN 'Soin visage pour une routine quotidienne simple.'
            WHEN 'soins-cheveux' THEN 'Soin cheveux pour apporter douceur et nutrition.'
            WHEN 'coffrets-cadeaux' THEN 'Coffret cadeau pret a offrir.'
            WHEN 'luxe' THEN 'Piece premium avec finitions haut de gamme.'
        END AS description,

        CASE
            WHEN c.slug IN ('t-shirts','chaussettes') THEN ROUND((9.90 + ((gs % 20) * 1.5))::numeric, 2)
            WHEN c.slug IN ('polos','chemises','pulls','sweats','shorts','jupes') THEN ROUND((24.90 + ((gs % 35) * 2.2))::numeric, 2)
            WHEN c.slug IN ('jeans','pantalons','chinos','robes','combinaisons','leggings') THEN ROUND((29.90 + ((gs % 45) * 2.7))::numeric, 2)
            WHEN c.slug IN ('vestes','manteaux','doudounes','blazers') THEN ROUND((59.90 + ((gs % 70) * 3.8))::numeric, 2)
            WHEN c.slug IN ('sneakers','running','chaussures-ville','bottines','sandales','escarpins','mocassins','chaussures-randonnee') THEN ROUND((39.90 + ((gs % 80) * 3.6))::numeric, 2)
            WHEN c.slug IN ('sacs-a-main','sacs-a-dos','sacs-de-voyage','montres','lunettes-soleil') THEN ROUND((19.90 + ((gs % 90) * 2.9))::numeric, 2)
            WHEN c.slug IN ('portefeuilles','ceintures','casquettes','bonnets','echarpes','bijoux','sous-vetements','pyjamas','maillots-de-bain') THEN ROUND((12.90 + ((gs % 40) * 2.1))::numeric, 2)
            WHEN c.slug IN ('tenues-sport','brassieres-sport','yoga','accessoires-tech','coques-housses') THEN ROUND((14.90 + ((gs % 60) * 2.4))::numeric, 2)
            WHEN c.slug IN ('parfums','soins-visage','soins-cheveux','coffrets-cadeaux') THEN ROUND((11.90 + ((gs % 55) * 2.6))::numeric, 2)
            WHEN c.slug = 'luxe' THEN ROUND((149.90 + ((gs % 120) * 6.5))::numeric, 2)
            ELSE ROUND((19.90 + ((gs % 30) * 2.0))::numeric, 2)
        END AS price,

        5 + (gs % 96) AS stock,
        c.id AS category_id,
        TRUE AS is_active
    FROM generate_series(1, 100000) AS gs
    JOIN catalog_category c
      ON c.id = ((gs - 1) % 50) + 1
    CROSS JOIN brands
    CROSS JOIN colors
    CROSS JOIN materials
    CROSS JOIN fits
    CROSS JOIN LATERAL (
        SELECT
            brands.arr[((gs - 1) % array_length(brands.arr, 1)) + 1] AS b,
            colors.arr[((gs * 3 - 1) % array_length(colors.arr, 1)) + 1] AS col,
            materials.arr[((gs * 5 - 1) % array_length(materials.arr, 1)) + 1] AS mat,
            fits.arr[((gs * 7 - 1) % array_length(fits.arr, 1)) + 1] AS f
    ) v
    RETURNING 1
)
SELECT COUNT(*) FROM insert_products;

COMMIT;
--------


ORDER

BEGIN;

TRUNCATE TABLE order_products, orders_orderline, orders_order RESTART IDENTITY CASCADE;

CREATE TEMP TABLE tmp_selected_customers AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS rn,
    customer_id
FROM (
    SELECT gs AS customer_id
    FROM generate_series(1, 10000) AS gs
    ORDER BY random()
    LIMIT 9000
) t;

CREATE TEMP TABLE tmp_orders_seed AS
SELECT
    gs AS order_no,
    CASE
        WHEN gs <= 9000 THEN sc.customer_id
        ELSE (SELECT customer_id
              FROM tmp_selected_customers
              WHERE rn = 1 + floor(random() * 9000)::int)
    END AS customer_id
FROM generate_series(1, 20000) AS gs
LEFT JOIN tmp_selected_customers sc
    ON sc.rn = gs;

INSERT INTO orders_order (customer_id, status, total_amount, created_at)
SELECT
    customer_id,
    'confirmed',
    0.00,
    now()
    - ((floor(random() * 180))::int || ' days')::interval
    - ((floor(random() * 86400))::int || ' seconds')::interval
FROM tmp_orders_seed
ORDER BY order_no;

CREATE TEMP TABLE tmp_line_seed AS
SELECT
    o.id AS order_id,
    item_idx,
    ((o.id * 7919 + item_idx * 4729) % 100000 + 1)::int AS product_id,
    (1 + floor(random() * 4))::int AS quantity
FROM orders_order o
JOIN generate_series(1, 15) AS item_idx
    ON item_idx <= (1 + floor(random() * 15))::int;

INSERT INTO orders_orderline (order_id, product_id, product_name, unit_price, quantity, line_total)
SELECT
    order_id,
    product_id,
    'Produit catalogue #' || product_id,
    round((9.90 + ((product_id % 250) * 1.37))::numeric, 2) AS unit_price,
    quantity,
    round((round((9.90 + ((product_id % 250) * 1.37))::numeric, 2) * quantity)::numeric, 2) AS line_total
FROM tmp_line_seed;

INSERT INTO order_products (order_id, product_id)
SELECT DISTINCT
    order_id,
    product_id
FROM tmp_line_seed;

UPDATE orders_order o
SET total_amount = totals.total_amount
FROM (
    SELECT
        order_id,
        round(sum(line_total)::numeric, 2) AS total_amount
    FROM orders_orderline
    GROUP BY order_id
) totals
WHERE o.id = totals.order_id;

COMMIT;




-----
ROLLBACK;
BEGIN;

TRUNCATE TABLE order_products, orders_orderline, orders_order RESTART IDENTITY CASCADE;

CREATE TEMP TABLE tmp_selected_customers AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS rn,
    customer_id
FROM (
    SELECT gs AS customer_id
    FROM generate_series(1, 10000) AS gs
    ORDER BY random()
    LIMIT 9000
) t;

CREATE TEMP TABLE tmp_orders_seed AS
SELECT
    gs AS order_no,
    CASE
        WHEN gs <= 9000 THEN sc.customer_id
        ELSE (
            SELECT customer_id
            FROM tmp_selected_customers
            ORDER BY random()
            LIMIT 1
        )
    END AS customer_id
FROM generate_series(1, 20000) AS gs
LEFT JOIN tmp_selected_customers sc
    ON sc.rn = gs;

INSERT INTO orders_order (customer_id, status, total_amount, created_at)
SELECT
    customer_id,
    'confirmed',
    0.00,
    now()
    - ((floor(random() * 180))::int || ' days')::interval
    - ((floor(random() * 86400))::int || ' seconds')::interval
FROM tmp_orders_seed
ORDER BY order_no;

CREATE TEMP TABLE tmp_line_seed AS
SELECT
    o.id AS order_id,
    item_idx,
    ((o.id * 7919 + item_idx * 4729) % 100000 + 1)::int AS product_id,
    (1 + floor(random() * 4))::int AS quantity
FROM orders_order o
JOIN generate_series(1, 15) AS item_idx
    ON item_idx <= (1 + floor(random() * 15))::int;

INSERT INTO orders_orderline (order_id, product_id, product_name, unit_price, quantity, line_total)
SELECT
    order_id,
    product_id,
    'Produit catalogue #' || product_id,
    round((9.90 + ((product_id % 250) * 1.37))::numeric, 2) AS unit_price,
    quantity,
    round((round((9.90 + ((product_id % 250) * 1.37))::numeric, 2) * quantity)::numeric, 2) AS line_total
FROM tmp_line_seed;

INSERT INTO order_products (order_id, product_id)
SELECT DISTINCT
    order_id,
    product_id
FROM tmp_line_seed;

UPDATE orders_order o
SET total_amount = totals.total_amount
FROM (
    SELECT
        order_id,
        round(sum(line_total)::numeric, 2) AS total_amount
    FROM orders_orderline
    GROUP BY order_id
) totals
WHERE o.id = totals.order_id;

COMMIT;

-----



BEGIN;

TRUNCATE TABLE order_products, orders_orderline, orders_order RESTART IDENTITY CASCADE;

CREATE TEMP TABLE tmp_selected_customers AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS rn,
    customer_id
FROM (
    SELECT gs AS customer_id
    FROM generate_series(1, 10000) AS gs
    ORDER BY random()
    LIMIT 9000
) t;

CREATE TEMP TABLE tmp_orders_seed AS
SELECT
    gs AS order_no,
    CASE
        WHEN gs <= 9000 THEN sc.customer_id
        ELSE (
            SELECT customer_id
            FROM tmp_selected_customers
            WHERE rn = 1 + floor(random() * 9000)::int
        )
    END AS customer_id
FROM generate_series(1, 20000) AS gs
LEFT JOIN tmp_selected_customers sc
    ON sc.rn = gs;

INSERT INTO orders_order (customer_id, status, total_amount, created_at)
SELECT
    customer_id,
    'confirmed',
    NULL,
    now()
    - ((floor(random() * 180))::int || ' days')::interval
    - ((floor(random() * 86400))::int || ' seconds')::interval
FROM tmp_orders_seed
ORDER BY order_no;

CREATE TEMP TABLE tmp_order_item_counts AS
SELECT
    id AS order_id,
    (1 + floor(random() * 15))::int AS item_count
FROM orders_order;

CREATE TEMP TABLE tmp_line_seed AS
SELECT
    oic.order_id,
    item_idx,
    ((oic.order_id * 7919 + item_idx * 4729) % 100000 + 1)::int AS product_id,
    (1 + floor(random() * 4))::int AS quantity
FROM tmp_order_item_counts oic
JOIN generate_series(1, 15) AS item_idx
    ON item_idx <= oic.item_count;

INSERT INTO orders_orderline (order_id, product_id, product_name, unit_price, quantity, line_total)
SELECT
    order_id,
    product_id,
    'Produit catalogue #' || product_id,
    round((9.90 + ((product_id % 250) * 1.37))::numeric, 2) AS unit_price,
    quantity,
    round((round((9.90 + ((product_id % 250) * 1.37))::numeric, 2) * quantity)::numeric, 2) AS line_total
FROM tmp_line_seed;

INSERT INTO order_products (order_id, product_id)
SELECT DISTINCT
    order_id,
    product_id
FROM tmp_line_seed;

COMMIT;