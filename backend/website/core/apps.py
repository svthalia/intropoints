# myapp/apps.py
from django.apps import AppConfig

# --------------- #
# Main App Config #
# --------------- #


# This defines the main application that
# runs the website
class WebsiteConfig(AppConfig):
    """
    Main app configuration for the website.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """
        Mainly override in order to hide certain
        admin models.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        from django.contrib import admin
        from django.contrib.auth.models import Group
        from oauth2_provider.models import AccessToken, Grant, IDToken, RefreshToken

        # Unregister unwanted apps
        admin.site.unregister(AccessToken)
        admin.site.unregister(Grant)
        admin.site.unregister(IDToken)
        admin.site.unregister(RefreshToken)

        admin.site.unregister(Group)
