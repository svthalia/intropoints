from django.contrib import admin

from stores.models.stores import Store

# ----------------- #
# Store Admin Panel #
# ----------------- #


@admin.register(Store)
class StoreAdminPanel(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the Store model.

    ----

    **Contains** the options:

    - ``list_display``: The display fields in the admin panel list
    - ``list_filter``: The filter fields in the admin panel list
    - ``search_field``: The fields that are searchable
    """

    list_display = ("name", "tournament")

    list_filter = ("name", "tournament__name")

    search_fields = ("name", "tournament__name")

    # -------------- #
    # Custom inlines #
    # -------------- #

    def get_inlines(self, request, obj=None):
        """
        Retrieves the inlines for the admin panel.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :param obj: The store instance
        :type obj: Store

        :return: The tabular inlines
        :rtype: list
        """

        from stores.admin.items import ItemAdminInlineTab

        return [ItemAdminInlineTab]
