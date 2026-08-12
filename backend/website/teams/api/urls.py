from django.urls import path

from teams.api.views.base import AllTeamsAPIView, CurrentTeamAPIView, SelectTeamAPIView
from teams.api.views.inventory import CurrentTeamInventoryForTournamentAPIView, CurrentTeamUseItemForAPIView
from teams.api.views.scoreboard import MainScoreboard as MainTeamScoreboardAPIView
from teams.api.views.scoreboard import TournamentScoreboard as TournamentTeamScoreboardAPIView

app_name = "teams_api"

# Team url patters for easy team attribute
# retrieval and manipulation
#
#
# ``/api/teams/all/``
#   -> Get a list of ALL teams
#
# ``/api/teams/select/<int:id>/``
#   -> Select a single team by its id
#
# ``/api/teams/current/
#   -> Get the team that the user is currently int
#
#
# ``/api/teams/current/inventory-for/<slug:slug>/
#   -> Get a team's inventory for a given tournament
#
# ``/api/teams/current/use-item/<int:id>/
#   -> Use the item with the given id
#
#
# ``/api/teams/main-scoreboard/
#   -> Top 3 teams overall
#
# ``/api/teams/tournament-scoreboard-for/<slug:slug>/
#   -> Top 3 teams for the given tournament

urlpatterns = [
    path("all/", AllTeamsAPIView.as_view(), name="teams_all"),
    path("select/<int:id>/", SelectTeamAPIView.as_view(), name="teams_select"),
    path("current/", CurrentTeamAPIView.as_view(), name="teams_current"),
    # Inventory endpoints
    path(
        "current/inventory-for/<slug:slug>/",
        CurrentTeamInventoryForTournamentAPIView.as_view(),
        name="teams_current_inventory",
    ),
    path("current/use-item/<int:id>/", CurrentTeamUseItemForAPIView.as_view(), name="teams_current_use_item"),
    # Scoreboard endpoints
    path(
        "main-scoreboard/",
        MainTeamScoreboardAPIView.as_view(),
        name="teams_main_scoreboard",
    ),
    path(
        "tournament-scoreboard-for/<slug:slug>/",
        TournamentTeamScoreboardAPIView.as_view(),
        name="teams_main_scoreboard",
    ),
]
