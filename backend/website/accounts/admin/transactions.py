from django.contrib import admin
from django.utils.html import format_html

from accounts.models.transactions import AdminTransaction, Transaction

# ----------------------- #
# Transaction Admin Panel #
# ----------------------- #


# Transaction should be mainly immutable, except
# the essential administrative ones, hence
# the only display they should have is an inline
# within some account.
class TransactionInline(admin.TabularInline):
    """
    Transaction inline model for displaying transactions
    per account if needed.

    ----

    **Contains** the settings:

    - ``model`` The inline model - ``Transaction``
    - ``extra``: The amount of extra rows to show
    - ``fields`` The fields to show
    - ``readonly_fields``: The fields that should not be editable
    - ``can_delete``: Whether transactions can be deleted
    """

    model = Transaction
    extra = 0
    verbose_name_plural = "Transaction Ledger"
    can_delete = False

    fields = ("amount", "accepted", "requested_at", "reverse")
    readonly_fields = fields

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def has_add_permission(self, request, obj=None):
        """
        Determines whether the user can add new objects onto
        the inline view

        ----

        In this case, normal transactions can never be removed.

        ----

        @param request -> the HTTP(s) request being made;
        @param obj     -> the parent account object;
        @return        -> always false;
        """

        return False

    # ------------------------ #
    # Additional Functionality #
    # ------------------------ #

    def reverse(self, obj):
        """
        Property that creates a revert option for transactions.
        Simply redirects to the rever view for the process to begin.

        ----

        :param obj: The selected transaction
        :type obj: Transaction

        :return: The button HTML component in a string
        :rtype: SafeString
        """

        if obj.id and obj.accepted:
            return format_html(f'<a class="button" href="revert/{obj.id}/">Revert</a>')
        return ""


# -------------------------------------- #
# Administrative Transaction Admin Panel #
# -------------------------------------- #


# These sort of transactions is the only
# ones that should have a single-display admin panel.
# The reason is to have an endpoint for creating them,
# and since we only want admins to do so, it only makes
# sense to do it in the admin control panel.
@admin.register(AdminTransaction)
class AdminTransactionAdmin(admin.ModelAdmin):
    """
    Administrative transaction admin panel scheme.
    It is only used for **CREATING** and not **DELETING**
    such transactions.

    ----

    **Contains** the fields:

    - ``fields``: The fields editable fields
    - ``list_display``: The fields to display in a list display
    """

    fields = ("account", "amount")

    list_display = ("description", "requested_at")

    # ------------ #
    # Base methods #
    # ------------ #

    def has_change_permission(self, request, obj=None):
        """
        Determines whether the user can change objects from the view.

        Transactions should never be edited! They are proof of commitment!

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param obj: The transaction instance
        :type obj: Account

        :return: Always false
        :rtype: bool
        """

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Determines whether the user can delete objects from the view.

        ----

        Transactions should never be removed, only reverted!

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param obj: The transaction instance
        :type obj: AdminTransaction

        :return: Always false
        :rtype: bool
        """

        return False

    # --------------------- #
    # Display Functionality #
    # --------------------- #

    @admin.display(description="Description")
    def description(self, obj):
        """
        Determines how to retrieve the description of
        the transaction.

        ----

        :param obj: The transaction instance
        :type obj: AdminTransaction

        :return: The transaction's description
        :rtype: str
        """

        return obj.__str__()
