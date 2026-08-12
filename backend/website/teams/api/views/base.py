from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated

from teams import models
from teams.api.serializers import RetrievalSerializer as TeamRetrievalSerializer
from teams.api.utils import TeamAPIUtilities

# ------------------ #
# Retrieve all Teams #
# ------------------ #


class AllTeamsAPIView(ListAPIView):
    """
    Retrieves a list of all teams that are
    present within the app.
    """

    queryset = models.Team.objects.all()

    serializer_class = TeamRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ("tournaments", "members")
    search_fields = ("name",)
    ordering_fields = ["name", "latest_transaction"]

    filter_backends = [DjangoFilterBackend]


# -------------- #
# Single Select  #
# -------------- #


class SelectTeamAPIView(RetrieveAPIView):
    """
    Retrieves a single team by its id that is
    sent within the request url.
    """

    queryset = models.Team.objects.all()
    lookup_field = "id"

    serializer_class = TeamRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]


# ---------------------- #
# Current team retrieval #
# ---------------------- #


class CurrentTeamAPIView(RetrieveAPIView):
    """
    Retrieves the team of the user that has made
    the api request.
    """

    queryset = models.Team.objects.all()

    serializer_class = TeamRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    def get_object(self):
        """
        Get the user from the request, find it's team
        and return it by serializing it into a proper
        API response.
        """

        return TeamAPIUtilities.get_team_from_request(self.request)
