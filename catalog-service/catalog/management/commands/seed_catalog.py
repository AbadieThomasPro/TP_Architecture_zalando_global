from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Seed catalog categories and products for local/test environments"

    @transaction.atomic
    def handle(self, *args, **options):
        sneakers, _ = Category.objects.get_or_create(
            slug="sneakers",
            defaults={"name": "Sneakers"},
        )
        vestes, _ = Category.objects.get_or_create(
            slug="vestes",
            defaults={"name": "Vestes"},
        )
        accessoires, _ = Category.objects.get_or_create(
            slug="accessoires",
            defaults={"name": "Accessoires"},
        )

        # required_slugs = {
        #     "nike-air-zoom",
        #     "adidas-forum-low",
        #     "puma-rider",
        #     "veste-en-jean",
        #     "doudoune-legere",
        #     "sac-sport",
        #     "casquette-noire",
        #     "chaussettes-running",
        # }
        # Product.objects.exclude(slug__in=required_slugs).delete()

        Product.objects.update_or_create(
            slug="nike-air-zoom",
            defaults={
                "name": "Nike Air Zoom",
                "description": "Chaussure de running légère",
                "price": "129.90",
                "stock": 12,
                "category": sneakers,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="adidas-forum-low",
            defaults={
                "name": "Adidas Forum Low",
                "description": "Sneaker lifestyle en cuir",
                "price": "109.90",
                "stock": 10,
                "category": sneakers,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="puma-rider",
            defaults={
                "name": "Puma Rider",
                "description": "Sneaker retro et confortable",
                "price": "99.90",
                "stock": 8,
                "category": sneakers,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="veste-en-jean",
            defaults={
                "name": "Veste en jean",
                "description": "Veste en denim coupe droite",
                "price": "79.90",
                "stock": 7,
                "category": vestes,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="doudoune-legere",
            defaults={
                "name": "Doudoune légère",
                "description": "Doudoune compacte mi-saison",
                "price": "119.90",
                "stock": 6,
                "category": vestes,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="sac-sport",
            defaults={
                "name": "Sac sport",
                "description": "Sac polyvalent 35L",
                "price": "49.90",
                "stock": 25,
                "category": accessoires,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="casquette-noire",
            defaults={
                "name": "Casquette noire",
                "description": "Casquette classique ajustable",
                "price": "24.90",
                "stock": 30,
                "category": accessoires,
                "is_active": True,
            },
        )
        Product.objects.update_or_create(
            slug="chaussettes-running",
            defaults={
                "name": "Chaussettes running",
                "description": "Paire respirante anti-frottement",
                "price": "14.90",
                "stock": 40,
                "category": accessoires,
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Catalog seed completed."))
