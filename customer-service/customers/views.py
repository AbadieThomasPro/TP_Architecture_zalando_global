from rest_framework import generics
from django.http import JsonResponse
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer, AddressCreateSerializer


class CustomerListView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        queryset = Customer.objects.all()
        email = self.request.query_params.get("email")

        if email:
            queryset = queryset.filter(email=email)

        return queryset


class CustomerDetailView(generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class CustomerAddressesView(generics.ListAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(customer_id=self.kwargs["pk"])


class AddressCreateView(generics.CreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressCreateSerializer

def health_check(request):
    return JsonResponse({"status": "ok"})