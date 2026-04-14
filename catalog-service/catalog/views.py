from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


@extend_schema(
    tags=["Categories"],
    summary="Lister les categories",
    description="Retourne toutes les categories du catalogue.",
    responses={
        200: OpenApiResponse(
            response=CategorySerializer(many=True),
            description="Liste des categories.",
        )
    },
    examples=[
        OpenApiExample(
            "Categories response",
            value=[
                {"id": 1, "name": "Sneakers", "slug": "sneakers"},
                {"id": 2, "name": "Vestes", "slug": "vestes"},
            ],
            response_only=True,
        )
    ],
)
class CategoryListView(generics.ListAPIView):
    """Expose la liste complete des categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(
    tags=["Products"],
    summary="Lister les produits",
    description=(
        "Retourne tous les produits. Bonus: supporte le filtrage par categorie "
        "et la recherche par nom."
    ),
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filtre par slug de categorie (ex: sneakers).",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Recherche partielle sur le nom du produit.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductSerializer(many=True),
            description="Liste des produits.",
        )
    },
    examples=[
        OpenApiExample(
            "Products response",
            value=[
                {
                    "id": 1,
                    "name": "Nike Air Zoom",
                    "slug": "nike-air-zoom",
                    "description": "Chaussure de running legere",
                    "price": "129.90",
                    "stock": 12,
                    "category": {"id": 1, "name": "Sneakers", "slug": "sneakers"},
                    "is_active": True,
                }
            ],
            response_only=True,
        )
    ],
)
class ProductListView(generics.ListAPIView):
    """Expose tous les produits, avec filtrage categorie et recherche par nom."""

    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        category_slug = self.request.query_params.get("category")
        search = self.request.query_params.get("search")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


@extend_schema(
    tags=["Products"],
    summary="Lister les produits actifs",
    description="Bonus: retourne uniquement les produits actifs.",
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filtre par slug de categorie (ex: accessoires).",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Recherche partielle sur le nom du produit.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductSerializer(many=True),
            description="Liste des produits actifs.",
        )
    },
)
class ActiveProductListView(generics.ListAPIView):
    """Expose uniquement les produits actifs avec filtres optionnels."""

    queryset = Product.objects.filter(is_active=True).select_related("category")
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        category_slug = self.request.query_params.get("category")
        search = self.request.query_params.get("search")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


@extend_schema(
    tags=["Products"],
    summary="Detail d'un produit",
    description="Retourne le detail d'un produit actif via son identifiant.",
    responses={
        200: OpenApiResponse(
            response=ProductSerializer,
            description="Detail du produit.",
        ),
        404: OpenApiResponse(description="Produit non trouve."),
    },
)
class ProductDetailView(generics.RetrieveAPIView):
    """Expose le detail d'un produit actif."""

    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer


@extend_schema(
    tags=["Health"],
    summary="Health check",
    description="Verifie que le service catalog-service est joignable.",
    responses={200: OpenApiResponse(description="Service operationnel.")},
)
class HealthCheckView(APIView):
    """Endpoint de verification rapide du service."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "catalog-service"}, status=status.HTTP_200_OK)
