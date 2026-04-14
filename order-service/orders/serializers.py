from decimal import Decimal

from rest_framework import serializers

from .external_services import CatalogGateway, CustomerGateway, ExternalServiceError
from .models import Order, OrderLine


class OrderLineReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ('product_id', 'product_name', 'unit_price', 'quantity', 'line_total')


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'customer_id', 'status', 'total_amount', 'created_at')


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderLineReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'customer_id', 'status', 'total_amount', 'created_at', 'items')


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(min_value=1)
    items = OrderItemInputSerializer(many=True, allow_empty=False)

    def validate_customer_id(self, value):
        gateway = CustomerGateway()
        try:
            exists = gateway.customer_exists(value)
        except ExternalServiceError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if not exists:
            raise serializers.ValidationError('customer not found')
        return value

    def create(self, validated_data):
        catalog_gateway = CatalogGateway()
        items_payload = validated_data['items']
        lines_to_create = []
        total_amount = Decimal('0.00')

        for item in items_payload:
            try:
                product = catalog_gateway.get_product(item['product_id'])
            except ExternalServiceError as exc:
                raise serializers.ValidationError({'items': [str(exc)]}) from exc

            quantity = item['quantity']
            line_total = product.price * quantity
            total_amount += line_total
            lines_to_create.append(
                {
                    'product_id': product.id,
                    'product_name': product.name,
                    'unit_price': product.price,
                    'quantity': quantity,
                    'line_total': line_total,
                }
            )

        order = Order.objects.create(
            customer_id=validated_data['customer_id'],
            status=Order.Status.CONFIRMED,
            total_amount=total_amount,
        )

        OrderLine.objects.bulk_create([
            OrderLine(order=order, **line_data)
            for line_data in lines_to_create
        ])

        order.refresh_from_db()
        return order
