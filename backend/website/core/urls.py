from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from login.views.login_auth import AuthCallbackView, AuthStoreView
from login.views.logout_request import LogoutView

# Main Application URLs
#
# Defines the other interactions with
# the backend
#
# These are mainly used for the frontend
# to control application flow and logic

urlpatterns = [
    # Admin Panel
    path("admin/accounts/", include("accounts.admin.urls")),
    path("admin/", admin.site.urls),
    # API Endpoints
    path("api/", include("core.api.urls", namespace="api")),
    # Login main flow
    #
    # Login -> OAuth -> Auth Callback -> Auth Store (Credentials)
    path("login/", include("login.urls", namespace="login")),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("auth/callback/", AuthCallbackView.as_view(), name="auth_callback"),
    path("auth/store/", AuthStoreView.as_view(), name="auth_store"),
]

if settings.FILE_UPLOAD_STORAGE == settings.LOCAL_STORAGE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ---------------- #
# Admin Management #
# ---------------- #

# Simply changing the display name for the
# base administration site

admin.site.site_header = "SHW Administration"
admin.site.site_title = "SHW Admin"
admin.site.index_title = "SHW Admin Control"
