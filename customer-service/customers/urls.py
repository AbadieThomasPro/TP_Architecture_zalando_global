from django.urls import path
from .views import (
    CustomerListView,
    CustomerDetailView,
    CustomerAddressesView,
    AddressCreateView,
    health_check,
)

urlpatterns = [
    path("customers/", CustomerListView.as_view(), name="customer-list"),
    path("customers/<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
    path("customers/<int:pk>/addresses/", CustomerAddressesView.as_view(), name="customer-addresses"),
    path("addresses/", AddressCreateView.as_view(), name="address-create"),
    path("health/", health_check, name="health-check"),
]