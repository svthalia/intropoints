from django.apps import AppConfig

# ---------------- #
# Teams App Config #
# ---------------- #


class TeamConfig(AppConfig):
    """
    Main app configuration for teams.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "teams"
