from django.urls import path

from .views import ActiveProductListView, CategoryListView, HealthCheckView, ProductDetailView, ProductListView


urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/active/", ActiveProductListView.as_view(), name="active-product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
