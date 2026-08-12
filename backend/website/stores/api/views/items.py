# ------------------- #
# Retrieve all stores #
# ------------------- #
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from stores.api.serializers.items import ItemRetrievalSerializer
from stores.api.serializers.purchases import CreationSerializer as PurchaseCreationSerializer
from stores.models.items import Item, UsableItem


class AllAPIView(ListAPIView):
    """
    Retrieves a list of all items present in
    the application
    """

    queryset = Item.objects.all()

    serializer_class = ItemRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]


# --------------------- #
# Select items by store #
# --------------------- #


class ForStoreAPIView(ListAPIView):
    """
    Retrieves a list of all items for a given store.
    """

    serializer_class = ItemRetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(store_id=self.kwargs["store__id"])


# ------------ #
# Use an item  #
# ------------ #


class UseItemAPIView(APIView):
    """
    Use a usable item from an inventory.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, usable_item_id):
        usable_item = UsableItem.objects.get(id=usable_item_id)
        usable_item.use()

        return Response({"success": True})


# ----------------------- #
# Create an item purchase #
# ----------------------- #


class CreatePurchaseAPIView(CreateAPIView):
    """
    Creates a new purchase for a given item and
    a team. The item then gets stored inside the
    team's tournament inventory.
    """

    queryset = Item.objects.all()

    serializer_class = PurchaseCreationSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def post(self, request, *args, **kwargs):
        """
        Creates a purchase for a given item and team,
        and handles item storage.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
