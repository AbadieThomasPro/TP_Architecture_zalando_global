from django.contrib import admin

from .models import Order, OrderLine


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    inlines = [OrderLineInline]
