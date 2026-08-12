from django.apps import AppConfig

# -------------------- #
# Challenge app config #
# -------------------- #


class ChallengeConfig(AppConfig):
    """
    Main app configuration for challenges.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "challenges"

    def ready(self):

        # Import the custom signals, since django cannot
        # find them by default.
        import challenges.signals  # noqa: F401
