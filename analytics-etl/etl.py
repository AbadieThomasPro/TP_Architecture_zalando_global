import os
from collections import OrderedDict
from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor, execute_values


def get_conn(prefix: str):
    return psycopg2.connect(
        host=os.environ[f"{prefix}_DB_HOST"],
        port=os.environ[f"{prefix}_DB_PORT"],
        dbname=os.environ[f"{prefix}_DB_NAME"],
        user=os.environ[f"{prefix}_DB_USER"],
        password=os.environ[f"{prefix}_DB_PASSWORD"],
    )


def fetch_all(conn, query: str):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()


def create_target_schema(conn):
    ddl = """
    CREATE TABLE IF NOT EXISTS pays (
        id BIGSERIAL PRIMARY KEY,
        nom VARCHAR(100) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS categories (
        id BIGINT PRIMARY KEY,
        nom VARCHAR(120) NOT NULL,
        slug VARCHAR(140) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS produits (
        id BIGINT PRIMARY KEY,
        categorie_id BIGINT NOT NULL REFERENCES categories(id),
        nom VARCHAR(255) NOT NULL,
        slug VARCHAR(255) NOT NULL UNIQUE,
        description TEXT NOT NULL DEFAULT '',
        prix NUMERIC(10, 2) NOT NULL,
        stock INTEGER NOT NULL,
        actif BOOLEAN NOT NULL
    );

    CREATE TABLE IF NOT EXISTS dates (
        id BIGINT PRIMARY KEY,
        date_heure TIMESTAMPTZ NOT NULL UNIQUE,
        annee INTEGER NOT NULL,
        mois INTEGER NOT NULL,
        jour INTEGER NOT NULL,
        heure INTEGER NOT NULL,
        minute INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS commandes (
        id BIGSERIAL PRIMARY KEY,
        source_order_id BIGINT NOT NULL,
        source_order_line_id BIGINT NOT NULL UNIQUE,
        customer_id BIGINT NOT NULL,
        statut VARCHAR(20) NOT NULL,
        quantite INTEGER NOT NULL,
        prix_unitaire NUMERIC(10, 2) NOT NULL,
        montant_ligne NUMERIC(10, 2) NOT NULL,
        montant_commande NUMERIC(10, 2) NULL,
        pays_id BIGINT NOT NULL REFERENCES pays(id),
        produit_id BIGINT NOT NULL REFERENCES produits(id),
        date_id BIGINT NOT NULL REFERENCES dates(id)
    );

    CREATE INDEX IF NOT EXISTS idx_produits_categorie_id
        ON produits(categorie_id);

    CREATE INDEX IF NOT EXISTS idx_commandes_pays_id
        ON commandes(pays_id);

    CREATE INDEX IF NOT EXISTS idx_commandes_produit_id
        ON commandes(produit_id);

    CREATE INDEX IF NOT EXISTS idx_commandes_date_id
        ON commandes(date_id);
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()


def truncate_target(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                commandes,
                dates,
                produits,
                categories,
                pays
            RESTART IDENTITY CASCADE
            """
        )
    conn.commit()


def date_key(dt: datetime) -> int:
    truncated = dt.replace(second=0, microsecond=0)
    return int(truncated.strftime("%Y%m%d%H%M"))


def extract_customer_countries(customer_conn):
    rows = fetch_all(
        customer_conn,
        """
        WITH ranked_addresses AS (
            SELECT
                customer_id,
                country,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id
                    ORDER BY is_default DESC, id ASC
                ) AS rn
            FROM customers_address
        )
        SELECT customer_id, country
        FROM ranked_addresses
        WHERE rn = 1
        """,
    )
    return {row["customer_id"]: row["country"] for row in rows}


def extract_catalog(catalog_conn):
    categories = fetch_all(
        catalog_conn,
        """
        SELECT id, name, slug
        FROM catalog_category
        ORDER BY id
        """,
    )
    products = fetch_all(
        catalog_conn,
        """
        SELECT id, category_id, name, slug, description, price, stock, is_active
        FROM catalog_product
        ORDER BY id
        """,
    )
    return categories, products


def extract_order_lines(order_conn):
    return fetch_all(
        order_conn,
        """
        SELECT
            o.id AS order_id,
            o.customer_id,
            o.status,
            o.total_amount,
            o.created_at,
            ol.id AS order_line_id,
            ol.product_id,
            ol.unit_price,
            ol.quantity,
            ol.line_total
        FROM orders_order o
        JOIN orders_orderline ol
            ON ol.order_id = o.id
        ORDER BY o.id, ol.id
        """,
    )


def load_dimensions(target_conn, categories, products, customer_country_map, order_lines):
    country_names = OrderedDict()
    for country in customer_country_map.values():
        country_names[country or "Inconnu"] = None

    if not country_names:
        country_names["Inconnu"] = None

    with target_conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO pays (nom) VALUES %s",
            [(name,) for name in country_names.keys()],
            page_size=1000,
        )
    target_conn.commit()

    countries = fetch_all(target_conn, "SELECT id, nom FROM pays ORDER BY id")
    country_id_by_name = {row["nom"]: row["id"] for row in countries}

    with target_conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO categories (id, nom, slug) VALUES %s",
            [(row["id"], row["name"], row["slug"]) for row in categories],
            page_size=1000,
        )
        execute_values(
            cur,
            """
            INSERT INTO produits (id, categorie_id, nom, slug, description, prix, stock, actif)
            VALUES %s
            """,
            [
                (
                    row["id"],
                    row["category_id"],
                    row["name"],
                    row["slug"],
                    row["description"] or "",
                    row["price"],
                    row["stock"],
                    row["is_active"],
                )
                for row in products
            ],
            page_size=1000,
        )
    target_conn.commit()

    unique_dates = OrderedDict()
    for row in order_lines:
        created_at = row["created_at"].replace(second=0, microsecond=0)
        unique_dates[date_key(created_at)] = created_at

    if unique_dates:
        with target_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO dates (id, date_heure, annee, mois, jour, heure, minute)
                VALUES %s
                """,
                [
                    (
                        key,
                        dt,
                        dt.year,
                        dt.month,
                        dt.day,
                        dt.hour,
                        dt.minute,
                    )
                    for key, dt in unique_dates.items()
                ],
                page_size=1000,
            )
        target_conn.commit()

    return country_id_by_name


def load_fact_orders(target_conn, order_lines, customer_country_map, country_id_by_name):
    rows = []
    fallback_country_id = country_id_by_name.get("Inconnu")

    for row in order_lines:
        created_at = row["created_at"].replace(second=0, microsecond=0)
        country_name = customer_country_map.get(row["customer_id"], "Inconnu") or "Inconnu"
        country_id = country_id_by_name.get(country_name, fallback_country_id)
        rows.append(
            (
                row["order_id"],
                row["order_line_id"],
                row["customer_id"],
                row["status"],
                row["quantity"],
                row["unit_price"],
                row["line_total"],
                row["total_amount"],
                country_id,
                row["product_id"],
                date_key(created_at),
            )
        )

    if rows:
        with target_conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO commandes (
                    source_order_id,
                    source_order_line_id,
                    customer_id,
                    statut,
                    quantite,
                    prix_unitaire,
                    montant_ligne,
                    montant_commande,
                    pays_id,
                    produit_id,
                    date_id
                )
                VALUES %s
                """,
                rows,
                page_size=1000,
            )
        target_conn.commit()


def main():
    customer_conn = get_conn("CUSTOMER")
    catalog_conn = get_conn("CATALOG")
    order_conn = get_conn("ORDER")
    target_conn = get_conn("ANALYTICS")

    try:
        create_target_schema(target_conn)
        truncate_target(target_conn)

        customer_country_map = extract_customer_countries(customer_conn)
        categories, products = extract_catalog(catalog_conn)
        order_lines = extract_order_lines(order_conn)

        country_id_by_name = load_dimensions(
            target_conn,
            categories,
            products,
            customer_country_map,
            order_lines,
        )
        load_fact_orders(target_conn, order_lines, customer_country_map, country_id_by_name)

        print(
            "ETL termine: "
            f"{len(categories)} categories, "
            f"{len(products)} produits, "
            f"{len(country_id_by_name)} pays, "
            f"{len(order_lines)} lignes de commandes chargees."
        )
    finally:
        customer_conn.close()
        catalog_conn.close()
        order_conn.close()
        target_conn.close()


if __name__ == "__main__":
    main()
