from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from teams.api.serializers import ScoreboardSerializer as TeamScoreboardSerializer
from teams.models import Team
from tournaments.models import Tournament

# ---------------------------- #
# Retrieve the main scoreboard #
# ---------------------------- #


class MainScoreboard(ListAPIView):
    """
    Retrieves the top 3 teams that have earned
    the most points during the whole event.
    """

    serializer_class = TeamScoreboardSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_queryset(self):
        """
        Retrieves the top 3 teams along with their main
        account balance.
        """

        return (
            Team.objects.all()
            .prefetch_related("members")
            .annotate(points=F("team_account__balance"))
            .order_by("-points")[:3]
        )


# ---------------------------------- #
# Scoreboard for a single tournament #
# ---------------------------------- #


class TournamentScoreboard(ListAPIView):
    """
    Retrieves the top 3 teams that have earned
    the most points during a single tournament.
    """

    serializer_class = TeamScoreboardSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_queryset(self):
        """
        Retrieves the top 3 teams along with their tournament
        account balance.
        """

        tournament_slug = self.kwargs.get("slug")
        tournament = get_object_or_404(Tournament, slug=tournament_slug)

        return (
            Team.objects.all()
            .prefetch_related("members")
            .filter(Q(tournament_account__tournament=tournament) & Q(tournament_account__type="points"))
            .annotate(points=F("tournament_account__balance"))
            .order_by("-points")[:3]
        )
