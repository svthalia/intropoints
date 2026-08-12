from django.contrib import admin

from .models import User

# ---------------- #
# User Admin Panel #
# ---------------- #


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the User model.

    ----

    **Contains** the settings:

    - ``fields``: The editable fields
    - ``readonly_fields``: The readonly fields
    - ``list_display``: The display field
    """

    fields = ("username", "display_name", "initials", "profile_photo", "user_permissions")

    readonly_fields = (
        "username",
        "display_name",
        "initials",
    )

    list_display = (
        "username",
        "display_name",
        "profile_photo",
    )
