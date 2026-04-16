import random

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from faker import Faker

from customers.models import Customer, Address


class Command(BaseCommand):
    help = "Génère 10 000 customers répartis sur 30 pays"

    
    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE customers_address, customers_customer RESTART IDENTITY CASCADE;"
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "--total",
            type=int,
            default=10000,
            help="Nombre total de customers à générer"
        )

    def handle(self, *args, **options):
        total = options["total"]
        fake = Faker("fr_FR")

        countries = [
            "France", "Germany", "Spain", "Italy", "Belgium",
            "Netherlands", "Portugal", "Switzerland", "Austria", "Poland",
            "Sweden", "Norway", "Denmark", "Finland", "Ireland",
            "United Kingdom", "Czech Republic", "Greece", "Hungary", "Romania",
            "Bulgaria", "Croatia", "Slovakia", "Slovenia", "Luxembourg",
            "Estonia", "Latvia", "Lithuania", "Canada", "United States"
        ]

        batch_size = 1000
        customers_to_create = []

        self.stdout.write(self.style.WARNING(f"Création de {total} customers..."))

        # Génération des customers
        for i in range(total):
            first_name = fake.first_name()
            last_name = fake.last_name()

            # email unique
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"

            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=fake.phone_number()[:20],
                is_active=random.choice([True, True, True, True, False])
            )
            customers_to_create.append(customer)

            if len(customers_to_create) >= batch_size:
                Customer.objects.bulk_create(customers_to_create, batch_size=batch_size)
                customers_to_create = []
                self.stdout.write(f"{i + 1}/{total} customers créés")

        if customers_to_create:
            Customer.objects.bulk_create(customers_to_create, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS("Customers créés avec succès."))

        # Récupération des customers créés
        customers = list(Customer.objects.order_by("-id")[:total])
        customers.reverse()

        addresses_to_create = []

        self.stdout.write(self.style.WARNING("Création des adresses..."))

        for i, customer in enumerate(customers):
            country = countries[i % len(countries)]

            address = Address(
                customer=customer,
                street=fake.street_address(),
                postal_code=fake.postcode(),
                city=fake.city(),
                country=country,
                is_default=True
            )
            addresses_to_create.append(address)

            if len(addresses_to_create) >= batch_size:
                Address.objects.bulk_create(addresses_to_create, batch_size=batch_size)
                addresses_to_create = []
                self.stdout.write(f"{i + 1}/{total} adresses créées")

        if addresses_to_create:
            Address.objects.bulk_create(addresses_to_create, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS("Adresses créées avec succès."))
        self.stdout.write(self.style.SUCCESS("Seed terminé."))