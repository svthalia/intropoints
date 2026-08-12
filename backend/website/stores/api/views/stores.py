from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from stores.api.serializers.stores import RetrievalSerializer as StoreRetrievalSerializer
from stores.models.stores import Store

# ------------------- #
# Retrieve all stores #
# ------------------- #


class AllAPIView(ListAPIView):
    """
    Retrieves a list of all present application
    stores.
    """

    queryset = Store.objects.all()

    serializer_class = StoreRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]


# --------------------------- #
# Select stores by tournament #
# --------------------------- #


class ForTournamentAPIView(ListAPIView):
    """
    Retrieves a list of all stores for a given tournament.
    """

    serializer_class = StoreRetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Store.objects.filter(tournament__slug=self.kwargs["tournament__slug"])
