from decimal import Decimal
from django.db import models


class AnalyticsCustomer(models.Model):
    source_customer_id = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AnalyticsCategory(models.Model):
    source_category_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'analytics categories'

    def __str__(self):
        return self.name


class AnalyticsProduct(models.Model):
    source_product_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(AnalyticsCategory, on_delete=models.PROTECT, related_name='products')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AnalyticsOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    source_order_id = models.PositiveIntegerField(unique=True)
    source_customer_id = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AnalyticsOrder #{self.source_order_id}"


class AnalyticsOrderLine(models.Model):
    source_order_line_id = models.PositiveIntegerField(unique=True)
    order = models.ForeignKey(AnalyticsOrder, related_name='items', on_delete=models.CASCADE)
    source_product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"AnalyticsOrderLine #{self.source_order_line_id}"