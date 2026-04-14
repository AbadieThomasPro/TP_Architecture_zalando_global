from django.urls import path
from .views import CustomerListCreateView, CustomerDetailView, CustomerAddressesView, AddressCreateView

urlpatterns = [
    path("customers/", CustomerListCreateView.as_view(), name="customer-list"),
    path("customers/<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
    path("customers/<int:pk>/addresses/", CustomerAddressesView.as_view(), name="customer-addresses"),
    path("addresses/", AddressCreateView.as_view(), name="address-create"),
]