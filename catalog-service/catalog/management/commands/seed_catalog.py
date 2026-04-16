from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.text import slugify

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Supprime les données existantes et génère 50 catégories + 100000 produits"

    def handle(self, *args, **options):
        self.stdout.write("Suppression des données existantes...")

        with connection.cursor() as cursor:
            cursor.execute(
                "TRUNCATE TABLE catalog_product, catalog_category RESTART IDENTITY CASCADE;"
            )

        self.stdout.write(self.style.SUCCESS("Tables vidées, IDs remis à zéro."))

        self.stdout.write("Création des catégories...")
        categories = self.create_categories()

        self.stdout.write("Création des produits...")
        self.create_products(categories)

        self.stdout.write(self.style.SUCCESS("Seed terminé : 50 catégories et 100000 produits créés."))

    def create_categories(self):
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

        categories = [
            Category(name=name, slug=slugify(name))
            for name in category_names
        ]

        Category.objects.bulk_create(categories, batch_size=50)
        return list(Category.objects.all())

    def create_products(self, categories):
        adjectives = [
            "Premium", "Classic", "Advanced", "Smart", "Eco", "Ultra", "Portable",
            "Compact", "Professional", "Elegant", "Modern", "Durable", "Essential",
            "Wireless", "Heavy Duty", "Deluxe", "Performance", "Everyday", "Mini", "Max"
        ]

        nouns = [
            "Kit", "Device", "Set", "Pack", "Edition", "Model", "Series", "Tool",
            "System", "Accessory", "Collection", "Gear", "Solution", "Item", "Product"
        ]

        descriptions = [
            "High quality product for daily use.",
            "Designed for performance and reliability.",
            "A practical and efficient choice.",
            "Suitable for professional and personal needs.",
            "Carefully selected for excellent value.",
            "Built with durable materials and modern design.",
            "A versatile product for many situations.",
            "Optimized for comfort and convenience.",
        ]

        total_products = 100_000
        batch_size = 5000
        products_to_create = []

        for i in range(1, total_products + 1):
            category = categories[(i - 1) % len(categories)]

            adjective = random.choice(adjectives)
            noun = random.choice(nouns)

            name = f"{adjective} {category.name} {noun} {i}"
            slug = slugify(name)
            description = random.choice(descriptions)
            price = Decimal(str(round(random.uniform(5, 2000), 2)))
            stock = random.randint(0, 500)
            is_active = random.choice([True, True, True, True, False])

            products_to_create.append(
                Product(
                    name=name,
                    slug=slug,
                    description=description,
                    price=price,
                    stock=stock,
                    category=category,
                    is_active=is_active,
                )
            )

            if len(products_to_create) >= batch_size:
                Product.objects.bulk_create(products_to_create, batch_size=batch_size)
                products_to_create = []
                self.stdout.write(f"{i} produits créés...")

        if products_to_create:
            Product.objects.bulk_create(products_to_create, batch_size=batch_size)