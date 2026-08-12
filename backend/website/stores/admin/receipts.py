from django.contrib import admin

from stores.models.items import UsedItemReceipt

# ----------------------------- #
# Used Item Receipt Admin Panel #
# ----------------------------- #


@admin.register(UsedItemReceipt)
class UsedItemReceiptAdminPanel(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the UsedItemReceipt model.

    ----

    Mainly a way to review what items have been used
    in order to fulfil uses.

    ----

    **Contains** the options:

    - ``list_display``: The display fields in the admin panel list
    - ``list_filter``: The filter fields in the admin panel list
    - ``search_field``: The fields that are searchable
    """

    fields = ("viewed", "description")

    readonly_fields = ("description",)

    list_display = ("team", "item", "used_at")

    list_filter = ("team",)

    search_fields = ("team__name",)

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def has_change_permission(self, request, obj=None):
        """
        Whether the user has permission to delete the
        viewed item receipts.

        Once a receipt has been viewed, it should be left
        as proof of transaction

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :param obj: The receipt instance
        :type obj: stores.models.items.UsedItemReceipt

        :return: False only if it's not already viewed
        :rtype: bool
        """

        if obj is None:
            return False

        return not obj.viewed

    def has_add_permission(self, request):
        """
        Whether the user has permission to add to the
        viewed item receipts.

        Receipts should only be created on item used,
        and thus never created.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :return: Always False
        :rtype: bool
        """

        return

    def has_delete_permission(self, request, obj=None):
        """
        Whether the user has permission to delete the
        viewed item receipts.

        Receipts should be marked as viewed and never deleted.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :param obj: The receipt instance
        :type obj: stores.models.items.UsedItemReceipt

        :return: Always False
        :rtype: bool
        """

        return False

    # ----------------- #
    # Additional Fields #
    # ----------------- #

    @admin.display(description="Item description")
    def description(self, obj):
        """
        Retrieves the description of the receipt's
        inner item.

        ----

        :param obj: The receipt instance
        :type obj: stores.models.items.UsedItemReceipt

        :return: The description of the receipt
        :rtype: str
        """

        return obj.item.description
