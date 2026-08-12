from django.apps import AppConfig

# --------------- #
# User App Config #
# --------------- #


class UsersConfig(AppConfig):
    """
    Main app configuration for users.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
