from django.contrib.admin.views.decorators import staff_member_required
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

app_name = "api"

# Main api entry point
#
# Add the apps that have a valid API right
# here in order to have it accessible
#
# You can find most of the API entrypoints
# here
#
# ``/api/users/``
#   -> User links
#
# ``/api/challenges/``
#   -> Challenge links
#
# ``/api/tournaments/``
#   -> Tournament links
#
# ``/api/submissions/``
#   -> Submission links
#
# ``/api/files/``
#   -> File links
#
# ``/api/stores/``
#   -> Store links
#
#
# Then, you can also find the API
# documentation framework:
#
# ``/api/schema/``
#   -> Download the API schema
#
# ``/api/docs/``
#   -> API documentation page

urlpatterns = [
    # Base API endpoints
    path("users/", include("users.api.urls", namespace="users")),
    path("challenges/", include("challenges.api.urls", namespace="challenges")),
    path("tournaments/", include("tournaments.api.urls", namespace="tournaments")),
    path("submissions/", include("submissions.api.urls", namespace="submissions")),
    path("files/", include("files.api.urls", namespace="files")),
    path("teams/", include("teams.api.urls", namespace="teams")),
    path("stores/", include("stores.api.urls", namespace="stores")),
    path("accounts/", include("accounts.api.urls", namespace="accounts")),
    # Documentation for API; these should only be accessible for admins
    # and under development. The scope of this website is not large enough
    # for the API to be accessible outside itself
    path("schema/", staff_member_required(SpectacularAPIView.as_view()), name="schema"),
    path(
        "docs/",
        staff_member_required(SpectacularRedocView.as_view(url_name="api:schema", template_name="api/readonly.html")),
        name="documentation",
    ),
]
