from django.urls import path

from accounts.api.views import ForTeamTournamentAPIView, TransactionsForTeamTournamentAPIView

app_name = "accounts"

urlpatterns = [
    path(
        "tournament/for-team-and-tournament/<int:team_id>/<slug:tournament_slug>/",
        ForTeamTournamentAPIView.as_view(),
        name="tournament_accounts_for_team_tournament",
    ),
    path(
        "transactions/for-team-and-tournament/<int:team_id>/<slug:tournament_slug>/",
        TransactionsForTeamTournamentAPIView.as_view(),
        name="transactions_for_team_tournament",
    ),
]
