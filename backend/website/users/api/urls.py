from django.urls import path

from users.api.views import CurrentUserAPIView

app_name = "users_api"

# Main user API endpoints
#
#
# ``/api/users/me/
#   -> Retrieve the current user

urlpatterns = [
    path("me/", CurrentUserAPIView.as_view(), name="current_user"),
]
