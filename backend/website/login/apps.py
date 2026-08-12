from django.apps import AppConfig

# ---------------- #
# Login App Config #
# ---------------- #


class LoginConfig(AppConfig):
    """
    Main app configuration for login.

    ----

    Any custom initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "login"
