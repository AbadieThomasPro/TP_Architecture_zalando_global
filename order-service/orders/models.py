from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    customer_id = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk}'


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='order_products', on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()

    class Meta:
        db_table = 'order_products'
        constraints = [
            models.UniqueConstraint(fields=['order', 'product_id'], name='unique_order_product'),
        ]

    def __str__(self):
        return f'OrderProduct order={self.order_id} product={self.product_id}'


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'OrderLine #{self.pk} - product {self.product_id}'
