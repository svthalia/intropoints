from django.urls import path

from tournaments.api.views import AllAPIView as TournamentsAllAPIView
from tournaments.api.views import SelectAPIView as TournamentsSelectAPIView

app_name = "tournaments_api"

# Tournament endpoints for retrieving
# display information
#
#
# ``/api/tournaments/all/
#   -> Get all present tournaments
#
# ``/api/select/<slug:slug>/
#   -> Select a single tournament

urlpatterns = [
    path("all/", TournamentsAllAPIView.as_view(), name="tournaments_all"),
    path("select/<slug:slug>/", TournamentsSelectAPIView.as_view(), name="tournaments_select"),
]
