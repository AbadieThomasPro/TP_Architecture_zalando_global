import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection

from orders.models import Order, OrderLine, OrderProduct


class Command(BaseCommand):
    help = "Réinitialise la base order et génère des produits + commandes réalistes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--customers",
            type=int,
            default=10000,
            help="Nombre max d'IDs clients disponibles",
        )
        parser.add_argument(
            "--products",
            type=int,
            default=100000,
            help="Nombre max d'IDs produits disponibles",
        )
        parser.add_argument(
            "--active-products",
            type=int,
            default=12000,
            help="Nombre de produits ayant au moins un achat",
        )
        parser.add_argument(
            "--max-orders",
            type=int,
            default=50000,
            help="Nombre maximum de commandes à créer",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Taille des batchs",
        )

    def handle(self, *args, **options):
        customers_count = options["customers"]
        products_count = options["products"]
        active_products = options["active_products"]
        max_orders = options["max_orders"]
        batch_size = options["batch_size"]

        if active_products > products_count:
            self.stdout.write(
                self.style.ERROR("active-products ne peut pas être supérieur à products")
            )
            return

        self.stdout.write("Suppression des anciennes données...")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE
                    orders_orderline,
                    orders_order,
                    orders_orderproduct
                RESTART IDENTITY CASCADE;
                """
            )

        self.stdout.write(self.style.SUCCESS("Tables vidées, IDs remis à zéro."))

        self.stdout.write("Création des produits locaux dans order-service...")
        self.create_order_products(products_count=products_count, batch_size=5000)

        self.stdout.write("Construction de la répartition des achats...")
        product_purchase_targets = self.build_product_purchase_targets(
            products_count=products_count,
            active_products=active_products,
            max_orders=max_orders,
        )

        total_orders = sum(product_purchase_targets.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"{products_count} produits créés dans OrderProduct, "
                f"{len(product_purchase_targets)} produits auront des achats, "
                f"pour un total de {total_orders} commandes."
            )
        )

        self.stdout.write("Création des commandes et lignes...")
        self.generate_orders_and_lines(
            product_purchase_targets=product_purchase_targets,
            customers_count=customers_count,
            batch_size=batch_size,
        )

        self.stdout.write(self.style.SUCCESS("Seed terminé."))

    def create_order_products(self, products_count, batch_size):
        products_buffer = []

        for product_id in range(1, products_count + 1):
            category_name = self.get_category_name(product_id)
            product_name = self.generate_catalog_product_name(product_id)
            current_price = self.generate_price_for_product(product_id)
            is_active = random.random() < 0.9

            products_buffer.append(
                OrderProduct(
                    product_id=product_id,
                    name=product_name,
                    category_name=category_name,
                    current_price=current_price,
                    is_active=is_active,
                )
            )

            if len(products_buffer) >= batch_size:
                OrderProduct.objects.bulk_create(products_buffer, batch_size=batch_size)
                self.stdout.write(f"{product_id}/{products_count} produits créés...")
                products_buffer = []

        if products_buffer:
            OrderProduct.objects.bulk_create(products_buffer, batch_size=batch_size)
            self.stdout.write(f"{products_count}/{products_count} produits créés...")

    def build_product_purchase_targets(self, products_count, active_products, max_orders):
        chosen_products = random.sample(range(1, products_count + 1), active_products)
        random.shuffle(chosen_products)

        targets = {}
        current_total = 0

        for product_id in chosen_products:
            if current_total >= max_orders:
                break

            roll = random.random()

            if roll < 0.70:
                purchases = random.randint(1, 5)
            elif roll < 0.90:
                purchases = random.randint(6, 20)
            elif roll < 0.98:
                purchases = random.randint(21, 80)
            else:
                purchases = random.randint(81, 300)

            remaining = max_orders - current_total
            purchases = min(purchases, remaining)

            if purchases <= 0:
                break

            targets[product_id] = purchases
            current_total += purchases

        return targets

    def generate_orders_and_lines(self, product_purchase_targets, customers_count, batch_size):
        statuses = [
            Order.Status.DRAFT,
            Order.Status.CONFIRMED,
            Order.Status.CANCELLED,
        ]
        weights = [10, 75, 15]

        products_map = {
            product.product_id: product
            for product in OrderProduct.objects.filter(product_id__in=product_purchase_targets.keys())
        }

        orders_buffer = []
        line_payloads_buffer = []
        total_created_orders = 0

        for product_id, purchase_count in product_purchase_targets.items():
            product = products_map[product_id]

            for _ in range(purchase_count):
                customer_id = random.randint(1, customers_count)
                status = random.choices(statuses, weights=weights, k=1)[0]

                orders_buffer.append(
                    Order(
                        customer_id=customer_id,
                        status=status,
                        total_amount=Decimal("0.00"),
                    )
                )

                quantity = 1
                unit_price = product.current_price
                line_total = unit_price * quantity

                line_payloads_buffer.append(
                    {
                        "product_id": product.product_id,
                        "product_name": product.name,
                        "unit_price": unit_price,
                        "quantity": quantity,
                        "line_total": line_total,
                    }
                )

                if len(orders_buffer) >= batch_size:
                    created = self.flush_batch(orders_buffer, line_payloads_buffer)
                    total_created_orders += created
                    self.stdout.write(f"{total_created_orders} commandes créées...")

                    orders_buffer = []
                    line_payloads_buffer = []

        if orders_buffer:
            created = self.flush_batch(orders_buffer, line_payloads_buffer)
            total_created_orders += created
            self.stdout.write(f"{total_created_orders} commandes créées...")

    def flush_batch(self, orders_buffer, line_payloads_buffer):
        created_orders = Order.objects.bulk_create(orders_buffer, batch_size=len(orders_buffer))

        order_lines = []
        for order, payload in zip(created_orders, line_payloads_buffer):
            order_lines.append(
                OrderLine(
                    order=order,
                    product_id=payload["product_id"],
                    product_name=payload["product_name"],
                    unit_price=payload["unit_price"],
                    quantity=payload["quantity"],
                    line_total=payload["line_total"],
                )
            )

        OrderLine.objects.bulk_create(order_lines, batch_size=len(order_lines))
        return len(created_orders)

    def generate_price_for_product(self, product_id):
        rng = random.Random(product_id)
        return Decimal(str(round(rng.uniform(5, 500), 2)))

    def get_category_name(self, product_id):
        category_names = [
            "Electronics",
            "Books",
            "Clothing",
            "Shoes",
            "Home",
            "Garden",
            "Beauty",
            "Sports",
            "Toys",
            "Automotive",
            "Health",
            "Jewelry",
            "Groceries",
            "Music",
            "Movies",
            "Office",
            "Pets",
            "Baby",
            "Tools",
            "Gaming",
            "Furniture",
            "Kitchen",
            "Outdoor",
            "Travel",
            "Watches",
            "Bags",
            "Accessories",
            "Appliances",
            "Stationery",
            "Art",
            "Crafts",
            "Industrial",
            "Software",
            "Phones",
            "Tablets",
            "Computers",
            "Cameras",
            "Lighting",
            "Fitness",
            "Bicycles",
            "Motorcycles",
            "Smart Home",
            "Medical",
            "Food Supplements",
            "Laundry",
            "Decoration",
            "Storage",
            "Security",
            "Streaming",
            "Collectibles",
        ]

        index = product_id - 1
        return category_names[index % len(category_names)]

    def generate_catalog_product_name(self, product_id):
        category_name = self.get_category_name(product_id)

        adjectives = [
            "Premium",
            "Classic",
            "Advanced",
            "Smart",
            "Eco",
            "Ultra",
            "Portable",
            "Compact",
            "Professional",
            "Elegant",
            "Modern",
            "Durable",
            "Essential",
            "Wireless",
            "Heavy Duty",
            "Deluxe",
            "Performance",
            "Everyday",
            "Mini",
            "Max",
        ]

        nouns = [
            "Kit",
            "Device",
            "Set",
            "Pack",
            "Edition",
            "Model",
            "Series",
            "Tool",
            "System",
            "Accessory",
            "Collection",
            "Gear",
            "Solution",
            "Item",
            "Product",
        ]

        index = product_id - 1
        adjective = adjectives[index % len(adjectives)]
        noun = nouns[index % len(nouns)]

        return f"{adjective} {category_name} {noun} {product_id}"