from django.contrib import admin

from accounts.admin.transactions import TransactionInline
from accounts.models.accounts import TournamentAccount

# ------------------------ #
# Team Account Admin Panel #
# ------------------------ #


@admin.register(TournamentAccount)
class AccountAdmin(admin.ModelAdmin):
    """
    Team account admin panel for managing certain
    parts of an account, such as viewing the
    transaction ledger and editing it.

    ----

    **Contains** the settings:

    - ``fields``: The fields editable fields
    - ``readonly_fields``: The readonly fields
    - ``list_display``: The fields to display in a list display
    - ``inlines``: The included inline displays
    """

    fields = ("balance", "tournament", "team")

    readonly_fields = fields

    list_display = ("name", "balance", "team")

    inlines = [TransactionInline]
