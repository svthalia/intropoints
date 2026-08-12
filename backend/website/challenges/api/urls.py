from django.urls import path

from challenges.api.views import ChallengeAPIView, ChallengeListAPIView, ChallengeListForTournamentAPIView

app_name = "challenges_api"

# The url patters for the challenge API are sort-of
# designed with the idea that you are supposed to
# read them in order to figure out what they do.
#
# ``/api/challenges/all/``
#   -> Get a list of ALL challenges
#
# ``/api/challenges/for-tournament/<slug:slug>/``
#   -> Get a list of all challenges belonging to
#      the given tournament
#
# ``/api/challenges/select/<slug:slug>/``
#   -> Get the challenge instance selected by the
#      give slug

urlpatterns = [
    path("all/", ChallengeListAPIView.as_view(), name="all"),
    path("for-tournament/<slug:slug>/", ChallengeListForTournamentAPIView.as_view(), name="select-from-tournament"),
    path("select/<slug:slug>/", ChallengeAPIView.as_view(), name="select"),
]
