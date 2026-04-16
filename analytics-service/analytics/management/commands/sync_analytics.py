from django.core.management.base import BaseCommand
from django.db import connections

from analytics.models import (
    AnalyticsCategory,
    AnalyticsCustomer,
    AnalyticsOrder,
    AnalyticsOrderLine,
    AnalyticsProduct,
)


class Command(BaseCommand):
    help = "Synchronise toutes les données vers la base analytics"

    def handle(self, *args, **options):
        self.stdout.write("Nettoyage des tables analytics...")

        AnalyticsOrderLine.objects.all().delete()
        AnalyticsOrder.objects.all().delete()
        AnalyticsProduct.objects.all().delete()
        AnalyticsCategory.objects.all().delete()
        AnalyticsCustomer.objects.all().delete()

        self.sync_customers()
        self.sync_catalog()
        self.sync_orders()

        self.stdout.write(self.style.SUCCESS("Synchronisation analytics terminée."))

    # =========================
    # CUSTOMERS
    # =========================
    def sync_customers(self):
        self.stdout.write("Synchronisation des customers...")

        with connections['customer_source'].cursor() as cursor:
            cursor.execute("""
                SELECT
                    c.id,
                    c.first_name,
                    c.last_name,
                    c.email,
                    c.phone,
                    c.is_active,
                    a.country,
                    a.city,
                    a.postal_code
                FROM customers_customer c
                LEFT JOIN customers_address a
                    ON a.customer_id = c.id AND a.is_default = true
            """)
            rows = cursor.fetchall()

        objs = []
        for row in rows:
            objs.append(
                AnalyticsCustomer(
                    source_customer_id=row[0],
                    first_name=row[1],
                    last_name=row[2],
                    email=row[3],
                    phone=row[4],
                    is_active=row[5],
                    country=row[6] or "",
                    city=row[7] or "",
                    postal_code=row[8] or "",
                )
            )

        AnalyticsCustomer.objects.bulk_create(objs, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"{len(objs)} customers synchronisés."))

    # =========================
    # CATALOG
    # =========================
    def sync_catalog(self):
        self.stdout.write("Synchronisation des catégories...")

        with connections['catalog_source'].cursor() as cursor:
            cursor.execute("""
                SELECT id, name, slug
                FROM catalog_category
            """)
            category_rows = cursor.fetchall()

        categories = [
            AnalyticsCategory(
                source_category_id=row[0],
                name=row[1],
                slug=row[2],
            )
            for row in category_rows
        ]
        AnalyticsCategory.objects.bulk_create(categories, batch_size=1000)

        category_map = {
            c.source_category_id: c
            for c in AnalyticsCategory.objects.all()
        }

        self.stdout.write("Synchronisation des produits...")

        with connections['catalog_source'].cursor() as cursor:
            cursor.execute("""
                SELECT id, name, slug, description, price, stock, is_active, category_id
                FROM catalog_product
            """)
            product_rows = cursor.fetchall()

        products = []
        for row in product_rows:
            products.append(
                AnalyticsProduct(
                    source_product_id=row[0],
                    name=row[1],
                    slug=row[2],
                    description=row[3] or "",
                    price=row[4],
                    stock=row[5],
                    is_active=row[6],
                    category=category_map[row[7]],
                )
            )

        AnalyticsProduct.objects.bulk_create(products, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"{len(products)} produits synchronisés."))

    # =========================
    # ORDERS
    # =========================
    def sync_orders(self):
        self.stdout.write("Synchronisation des commandes...")

        with connections['order_source'].cursor() as cursor:
            cursor.execute("""
                SELECT id, customer_id, status, total_amount, created_at
                FROM orders_order
            """)
            order_rows = cursor.fetchall()

        orders = [
            AnalyticsOrder(
                source_order_id=row[0],
                source_customer_id=row[1],
                status=row[2],
                total_amount=row[3],
                created_at=row[4],
            )
            for row in order_rows
        ]

        AnalyticsOrder.objects.bulk_create(orders, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"{len(orders)} commandes synchronisées."))

        # Mapping pour relier les lignes
        order_map = {
            o.source_order_id: o
            for o in AnalyticsOrder.objects.all()
        }

        self.stdout.write("Synchronisation des lignes de commande...")

        with connections['order_source'].cursor() as cursor:
            cursor.execute("""
                SELECT id, order_id, product_id, product_name, unit_price, quantity, line_total
                FROM orders_orderline
            """)
            line_rows = cursor.fetchall()

        lines = []
        for row in line_rows:
            order = order_map.get(row[1])

            if not order:
                continue

            lines.append(
                AnalyticsOrderLine(
                    source_order_line_id=row[0],
                    order=order,
                    source_product_id=row[2],
                    product_name=row[3],
                    unit_price=row[4],
                    quantity=row[5],
                    line_total=row[6],
                )
            )

        AnalyticsOrderLine.objects.bulk_create(lines, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"{len(lines)} lignes synchronisées."))