from django.apps import AppConfig

# --------------------- #
# Tournament App Config #
# --------------------- #


class TournamentConfig(AppConfig):
    """
    Main app configuration for tournaments.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "tournaments"
