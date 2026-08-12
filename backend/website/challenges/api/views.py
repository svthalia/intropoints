from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated

from challenges.api.serializers import PreviewRetrievalSerializer as ChallengePreviewRetrievalSerializer
from challenges.api.serializers import RetrievalSerializer as ChallengeRetrievalSerializer
from challenges.models import Challenge

# ----------------------- #
# Retrieve all Challenges #
# ----------------------- #


class ChallengeListAPIView(ListAPIView):
    """
    View that handles retrieving all challenges'
    information in a serialized preview format via the
    Rest Framework.
    """

    serializer_class = ChallengePreviewRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_queryset(self):
        """
        Access all the available challenges.
        """

        return Challenge.objects.revealed().filter(enabled=True)


# ----------------- #
# Challenge Filters #
# ----------------- #


class ChallengeListForTournamentAPIView(ListAPIView):
    """
    View that handles retrieving all challenges'
    information in a serialized preview format for a
    specific tournament via the Rest Framework.
    """

    serializer_class = ChallengePreviewRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_queryset(self):
        """
        Accesses all the challenges matching the
        tournament slug given inside the URL.
        """

        tournament_slug = self.kwargs["slug"]
        return Challenge.objects.revealed().filter(tournament__slug=tournament_slug)


# ------------- #
# Single Select #
# ------------- #


class ChallengeAPIView(RetrieveAPIView):
    """
    View that handles retrieving a single challenge
    information in a serialized format for a
    given slug parameter via the Rest Framework.
    """

    serializer_class = ChallengeRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_object(self):
        """
        Searches for the challenge with the slug
        given inside the URL.
        """

        return Challenge.objects.get(slug=self.kwargs["slug"])
