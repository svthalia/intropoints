from django.apps import AppConfig

# --------------------- #
# Submission App Config #
# --------------------- #


class SubmissionConfig(AppConfig):
    """
    Main app configuration for teams.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "submissions"

    def ready(self):

        # Import the custom signals, since django cannot
        # find them by default.
        import submissions.signals  # noqa: F401
