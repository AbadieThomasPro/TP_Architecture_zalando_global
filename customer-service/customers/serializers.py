from rest_framework import serializers
from .models import Customer, Address


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "phone", "is_active"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "street", "postal_code", "city", "country", "is_default"]


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "customer", "street", "postal_code", "city", "country", "is_default"]