from django.apps import AppConfig

# ----------------- #
# Stores App Config #
# ----------------- #


class StoresConfig(AppConfig):
    """
    Main app configuration for teams.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "stores"
