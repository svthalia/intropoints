from django.apps import AppConfig

# ------------------ #
# Account App Config #
# ------------------ #


class AccountConfig(AppConfig):
    """
    Main app configuration for accounts.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
