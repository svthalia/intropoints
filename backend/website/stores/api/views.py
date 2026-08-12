from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from stores.api.serializers import (
    ItemRetrievalSerializer,
    PurchaseCreateSerializer,
    StoreSerializer,
)
from stores.models import Item, Purchase, Store


class ItemFilterSet(FilterSet):
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Item
        fields = ["store", "min_price", "max_price"]


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    lookup_field = "tournament__slug"
    lookup_url_kwarg = "slug"
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    lookup_field = "store__id"
    lookup_url_kwarg = "id"
    serializer_class = ItemRetrievalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ItemFilterSet
    search_fields = ["name", "description"]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ("team",)

    def get_serializer_class(self):
        if self.action == "create":
            return PurchaseCreateSerializer
        return None

    def get_queryset(self):
        user = self.request.user
        return Purchase.objects.filter(team__members=user)

    def create(self, request, *args, **kwargs):
        from rest_framework import status

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            if "insufficient" in str(e).lower():
                return Response(
                    {"error": "Insufficient coins for purchase"},
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )
            raise
