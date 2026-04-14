from dataclasses import dataclass
from decimal import Decimal

import requests
from django.conf import settings


class ExternalServiceError(Exception):
    pass


@dataclass
class ProductData:
    id: int
    name: str
    price: Decimal


class CustomerGateway:
    def customer_exists(self, customer_id: int) -> bool:
        if settings.USE_MOCK_SERVICES:
            return customer_id in {1, 2, 3}

        response = requests.get(f"{settings.CUSTOMER_SERVICE_URL}/api/customers/{customer_id}/", timeout=5)
        if response.status_code == 404:
            return False
        if not response.ok:
            raise ExternalServiceError('customer-service unavailable')
        return True


class CatalogGateway:
    mock_products = {
        1: ProductData(id=1, name='Nike Air Zoom', price=Decimal('129.90')),
        2: ProductData(id=2, name='Adidas Ultraboost', price=Decimal('149.90')),
        3: ProductData(id=3, name='Puma Rider', price=Decimal('39.90')),
    }

    def get_product(self, product_id: int) -> ProductData:
        if settings.USE_MOCK_SERVICES:
            product = self.mock_products.get(product_id)
            if not product:
                raise ExternalServiceError('product not found')
            return product

        response = requests.get(f"{settings.CATALOG_SERVICE_URL}/api/products/{product_id}/", timeout=5)
        if response.status_code == 404:
            raise ExternalServiceError('product not found')
        if not response.ok:
            raise ExternalServiceError('catalog-service unavailable')

        payload = response.json()
        return ProductData(
            id=payload['id'],
            name=payload['name'],
            price=Decimal(payload['price']),
        )
