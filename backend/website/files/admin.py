from django.contrib import admin

from files.models.base import File

# -------------------- #
# Base File Admin Form #
# -------------------- #


@admin.register(File)
class FileAdminPanel(admin.ModelAdmin):
    """
    Django admin interface for File model.

    Provides a view and management interface for uploaded files,
    including:

    ----

    **Contents** the settings:

    - ``list_display``: The fields to display in a list
    - ``search_fields``: The fields that can be searched for in a list
    """

    list_display = (
        "id",
        "name",
        "type",
        "is_compressed",
        "has_thumbnail",
    )

    search_fields = ("name",)

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def has_add_permission(self, request):
        """
        Overrides the basic function such that Files
        remain immutable.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :return: Always false
        :rtype: bool
        """

        # Files should never be added straight via
        # the Admin form.
        return False

    def has_change_permission(self, request, obj=None):
        """
        Overrides the basic function such that Files
        remain immutable.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param obj: The file object that was modified
        :type obj: files.models.base.File

        :return: Always false
        :rtype: bool
        """

        # Files should never be added straight via
        # the Admin form.
        return False
