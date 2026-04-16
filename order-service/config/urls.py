from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='order-schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='order-schema'), name='order-swagger-ui'),
    path('api/', include('orders.urls')),
]
