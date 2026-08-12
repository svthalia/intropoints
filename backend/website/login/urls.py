from django.urls import path

import login.views.login_callback as callback_views
import login.views.login_request as request_views
from login.views.login_start import StartLoginView

app_name = "login"

# This handles login within the backend
#
# The main flow is currently:
#
# 1. Start    - create the necessary OAuth redirect
# 2. OAuth    - catch the redirect and try to authenticate the user
# 3. Thalia   - catches the login requests and sends an OAuth request to
#               https://(staging.)thalia.nu/
# 4. Callback - catches the redirect from Thalia and registers the user in
#               the backend
# 5. Auth     - registers the credentials in a cookie for the frontend to use

urlpatterns = [
    # Base paths
    path("start/", StartLoginView.as_view(), name="login_start"),
    # Login providers
    path("thalia/", request_views.ThaliaLoginView.as_view(), name="login_thalia"),
    path("thalia/callback", callback_views.ThaliaCallbackView.as_view(), name="login_thalia_callback"),
]
