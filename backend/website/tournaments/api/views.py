from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated

from tournaments import models
from tournaments.api.serializers import RetrievalSerializer as TournamentRetrievalSerializer
from tournaments.models import Tournament

# ------------------------ #
# Retrieve all tournaments #
# ------------------------ #


class AllAPIView(ListAPIView):
    """
    View that handles retrieving all tournaments'
    information in a serialized format via the
    Rest Framework.
    """

    serializer_class = TournamentRetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters and retrieves all tournaments

        :return: The whole tournament queryset
        :rtype: TournamentQuerySet
        """

        return models.Tournament.objects.all()


# -------------------------- #
# Single selection retrieval #
# -------------------------- #


class SelectAPIView(RetrieveAPIView):
    """
    View that handles retrieving a specific tournament
    information in a serialized format via the Rest Framework.
    """

    serializer_class = TournamentRetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Tries to retrieve the tournament matching the given slug,
        if it exists

        ----

        :return: The tournament matching the given slug
        :rtype: Tournament
        """

        return Tournament.objects.get(slug=self.kwargs["slug"])
