from django.contrib import admin

from stores.models.purchases import Purchase


@admin.register(Purchase)
class PurchaseAdminPanel(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the Purchase model.

    ----

    **Contains** the options:

    - ``list_display``: The display fields in the admin panel list
    - ``list_filter``: The filter fields in the admin panel list
    - ``search_field``: The fields that are searchable
    """

    list_display = ("team", "item", "created_at")

    list_filter = ("created_at", "item__store")

    search_fields = ("team__name", "item__name")

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def has_change_permission(self, request, obj=None):
        """
        Whether the user has permission to edit the
        viewed purchases.

        Since a purchase serves as proof of transaction,
        it should never be tampered with.

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
        Whether the user has permission to add to the
        viewed purchases.

        Since a purchase serves as proof of transaction,
        it should never be forged. And there is no use in
        doing so.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :return: Always False
        :rtype: bool
        """

        return False
