from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from .models import Tournament

# ---------------------- #
# Tournament Admin Panel #
# ---------------------- #


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the Tournament model.

    ----

    **Contains** the settings:

    - ``fields``: The editable field
    - ``list_display``: The display field
    - ``search_fields``: The fields that are searchable
    - ``list_filter``: The allowed filters
    - ``prepopulated_fields``: The prepopulated fields on user input
    """

    fields = ("name", "slug", "active_from", "active_until")

    list_display = ("name", "active_from", "active_until")

    search_fields = ("name",)

    list_filter = (
        (
            "active_from",
            DateRangeFilter,
        ),
        (
            "active_until",
            DateRangeFilter,
        ),
    )

    prepopulated_fields = {"slug": ("name",)}
