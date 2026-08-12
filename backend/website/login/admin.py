from django.contrib import admin

from .models import OAuthUser

# ---------------------- #
# OAuth User Admin Panel #
# ---------------------- #

# Any other forms or models that
# handle login registration or tracking
# should be handled here.


# Register the imported users
@admin.register(OAuthUser)
class OAuthUserAdminPanel(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the OAuth User model.

    ----

    **Contains** the options:

    - ``list_display``: The display fields in the admin panel list
    - ``list_filter``: The filter fields in the admin panel list
    - ``search_field``: The fields that are searchable
    """

    list_display = ("user", "uid")

    search_fields = ("user__display_name", "uid")

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def has_change_permission(self, request, obj=None):
        """
        OAuth users should not be allowed to be changed, since
        they stand at the authentication's core.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :param obj: The purchase instance
        :type obj: stores.models.Purchase

        :return: Always False
        :rtype: bool
        """

        return False

    def has_add_permission(self, request):
        """
        OAuth Users should only be added through proper
        authentication.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :return: Always False
        :rtype: bool
        """

        return False
