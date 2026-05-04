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
    DROP TABLE IF EXISTS commandes CASCADE;
    DROP TABLE IF EXISTS dates CASCADE;
    DROP TABLE IF EXISTS produits CASCADE;
    DROP TABLE IF EXISTS categories CASCADE;
    DROP TABLE IF EXISTS pays CASCADE;

    CREATE TABLE IF NOT EXISTS dim_customer (
        customer_id BIGINT PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        email VARCHAR(254) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        is_active BOOLEAN NOT NULL,
        country VARCHAR(100) NOT NULL,
        city VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS dim_category (
        category_id BIGINT PRIMARY KEY,
        category_name VARCHAR(120) NOT NULL,
        category_slug VARCHAR(140) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS dim_product (
        product_id BIGINT PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        slug VARCHAR(255) NOT NULL UNIQUE,
        category_id BIGINT NOT NULL REFERENCES dim_category(category_id),
        category_name VARCHAR(120) NOT NULL,
        is_active BOOLEAN NOT NULL
    );

    CREATE TABLE IF NOT EXISTS dim_date (
        date_id BIGINT PRIMARY KEY,
        date TIMESTAMPTZ NOT NULL UNIQUE,
        day INTEGER NOT NULL,
        month INTEGER NOT NULL,
        month_name VARCHAR(20) NOT NULL,
        quarter INTEGER NOT NULL,
        year INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS fact_order_lines (
        fact_id BIGSERIAL PRIMARY KEY,
        order_id BIGINT NOT NULL,
        order_line_id BIGINT NOT NULL UNIQUE,
        customer_id BIGINT NOT NULL REFERENCES dim_customer(customer_id),
        product_id BIGINT NOT NULL REFERENCES dim_product(product_id),
        category_id BIGINT NOT NULL REFERENCES dim_category(category_id),
        date_id BIGINT NOT NULL REFERENCES dim_date(date_id),
        country VARCHAR(100) NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price NUMERIC(10, 2) NOT NULL,
        line_total NUMERIC(10, 2) NOT NULL,
        order_status VARCHAR(20) NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_dim_product_category_id
        ON dim_product(category_id);

    CREATE INDEX IF NOT EXISTS idx_fact_order_lines_customer_id
        ON fact_order_lines(customer_id);

    CREATE INDEX IF NOT EXISTS idx_fact_order_lines_product_id
        ON fact_order_lines(product_id);

    CREATE INDEX IF NOT EXISTS idx_fact_order_lines_category_id
        ON fact_order_lines(category_id);

    CREATE INDEX IF NOT EXISTS idx_fact_order_lines_date_id
        ON fact_order_lines(date_id);

    CREATE INDEX IF NOT EXISTS idx_fact_order_lines_country
        ON fact_order_lines(country);
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()


def truncate_target(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                fact_order_lines,
                dim_date,
                dim_product,
                dim_category,
                dim_customer
            RESTART IDENTITY CASCADE
            """
        )
    conn.commit()


def date_key(dt: datetime) -> int:
    return int(dt.strftime("%Y%m%d%H%M%S"))


def month_name(month: int) -> str:
    names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    return names[month]


def extract_customer_dimension(customer_conn):
    rows = fetch_all(
        customer_conn,
        """
        WITH ranked_addresses AS (
            SELECT
                customer_id,
                city,
                country,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id
                    ORDER BY is_default DESC, id ASC
                ) AS rn
            FROM customers_address
        )
        SELECT
            c.id AS customer_id,
            c.first_name,
            c.last_name,
            c.email,
            c.phone,
            c.is_active,
            COALESCE(ra.country, 'Inconnu') AS country,
            COALESCE(ra.city, 'Inconnue') AS city
        FROM customers_customer c
        LEFT JOIN ranked_addresses ra
            ON ra.customer_id = c.id
           AND ra.rn = 1
        ORDER BY c.id
        """,
    )
    return rows


def extract_category_dimension(catalog_conn):
    return fetch_all(
        catalog_conn,
        """
        SELECT id AS category_id, name AS category_name, slug AS category_slug
        FROM catalog_category
        ORDER BY id
        """,
    )


def extract_product_dimension(catalog_conn):
    return fetch_all(
        catalog_conn,
        """
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.slug,
            p.category_id,
            c.name AS category_name,
            p.is_active
        FROM catalog_product p
        JOIN catalog_category c
            ON c.id = p.category_id
        ORDER BY p.id
        """,
    )


def extract_fact_source(order_conn):
    return fetch_all(
        order_conn,
        """
        SELECT
            o.id AS order_id,
            o.customer_id,
            o.status AS order_status,
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


def load_dim_customer(target_conn, customers):
    with target_conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO dim_customer (
                customer_id, first_name, last_name, email, phone, is_active, country, city
            )
            VALUES %s
            """,
            [
                (
                    row["customer_id"],
                    row["first_name"],
                    row["last_name"],
                    row["email"],
                    row["phone"],
                    row["is_active"],
                    row["country"],
                    row["city"],
                )
                for row in customers
            ],
            page_size=1000,
        )
    target_conn.commit()


def load_dim_category(target_conn, categories):
    with target_conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO dim_category (category_id, category_name, category_slug)
            VALUES %s
            """,
            [
                (row["category_id"], row["category_name"], row["category_slug"])
                for row in categories
            ],
            page_size=1000,
        )
    target_conn.commit()


def load_dim_product(target_conn, products):
    with target_conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO dim_product (
                product_id, product_name, slug, category_id, category_name, is_active
            )
            VALUES %s
            """,
            [
                (
                    row["product_id"],
                    row["product_name"],
                    row["slug"],
                    row["category_id"],
                    row["category_name"],
                    row["is_active"],
                )
                for row in products
            ],
            page_size=1000,
        )
    target_conn.commit()


def load_dim_date(target_conn, fact_source_rows):
    unique_dates = OrderedDict()
    for row in fact_source_rows:
        created_at = row["created_at"].replace(microsecond=0)
        unique_dates[date_key(created_at)] = created_at

    with target_conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO dim_date (date_id, date, day, month, month_name, quarter, year)
            VALUES %s
            """,
            [
                (
                    key,
                    dt,
                    dt.day,
                    dt.month,
                    month_name(dt.month),
                    ((dt.month - 1) // 3) + 1,
                    dt.year,
                )
                for key, dt in unique_dates.items()
            ],
            page_size=1000,
        )
    target_conn.commit()


def load_fact_order_lines(target_conn, fact_source_rows, customer_country_by_id, product_category_by_id):
    with target_conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO fact_order_lines (
                order_id,
                order_line_id,
                customer_id,
                product_id,
                category_id,
                date_id,
                country,
                quantity,
                unit_price,
                line_total,
                order_status
            )
            VALUES %s
            """,
            [
                (
                    row["order_id"],
                    row["order_line_id"],
                    row["customer_id"],
                    row["product_id"],
                    product_category_by_id[row["product_id"]],
                    date_key(row["created_at"].replace(microsecond=0)),
                    customer_country_by_id.get(row["customer_id"], "Inconnu"),
                    row["quantity"],
                    row["unit_price"],
                    row["line_total"],
                    row["order_status"],
                )
                for row in fact_source_rows
                if row["product_id"] in product_category_by_id
            ],
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

        customers = extract_customer_dimension(customer_conn)
        categories = extract_category_dimension(catalog_conn)
        products = extract_product_dimension(catalog_conn)
        fact_source_rows = extract_fact_source(order_conn)

        load_dim_customer(target_conn, customers)
        load_dim_category(target_conn, categories)
        load_dim_product(target_conn, products)
        load_dim_date(target_conn, fact_source_rows)

        customer_country_by_id = {
            row["customer_id"]: row["country"] for row in customers
        }
        product_category_by_id = {
            row["product_id"]: row["category_id"] for row in products
        }
        load_fact_order_lines(
            target_conn,
            fact_source_rows,
            customer_country_by_id,
            product_category_by_id,
        )

        print(
            "ETL termine: "
            f"{len(customers)} clients, "
            f"{len(categories)} categories, "
            f"{len(products)} produits, "
            f"{len(fact_source_rows)} lignes de commande chargees."
        )
    finally:
        customer_conn.close()
        catalog_conn.close()
        order_conn.close()
        target_conn.close()


if __name__ == "__main__":
    main()
