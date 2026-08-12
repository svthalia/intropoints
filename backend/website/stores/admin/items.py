from django import forms
from django.contrib import admin

from stores.models.items import Item

# ---------------------------- #
# Custom Item Inline Tab Model #
# ---------------------------- #


class ItemAdminInlineTab(admin.TabularInline):
    """
    Item inline model for displaying items
    per store if needed.

    ----

    **Contains** the fields:

    - ``model`` The inline model - ``Item``
    - ``extra``: The amount of extra rows to show
    - ``fields`` The editable fields to show
    - ``readonly_fields``: The fields that should not be editable
    - ``can_delete``: Whether transactions can be deleted
    """

    model = Item
    extra = 0
    verbose_name_plural = "Stored Items"
    can_delete = False

    fields = ("name", "price", "description")
    readonly_fields = fields


# ---------------------- #
# Custom Item Admin Form #
# ---------------------- #


class ItemAdminForm(forms.ModelForm):
    """
    Class that represents a custom admin form
    for the Item model.

    Define how and what fields should be displayed.

    ----

    **Contains** the options:

    - ``thumbnail_source``: The thumbnail upload form

    ----

    The rest of the fields, along with the model are
    specified in the ``Meta`` class.
    """

    thumbnail_source = forms.FileField(
        required=False,
        help_text="Upload an item thumbnail (Optional)",
    )

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        model = Item
        fields = [
            "store",
            "name",
            "price",
            "description",
            "thumbnail_source",
        ]


# ---------------- #
# Item Admin Panel #
# ---------------- #


@admin.register(Item)
class ItemAdminPanel(admin.ModelAdmin):
    """
    Class that represents the admin panel
    configuration for the Item model.

    ----

    **Contains** the options:

    - ``list_display``: The display fields in the admin panel list
    - ``list_filter``: The filter fields in the admin panel list
    - ``search_field``: The fields that are searchable
    """

    list_display = ("name", "store", "price")

    list_filter = ("store",)

    search_fields = ("name", "description")

    # ----------------- #
    # Custom admin form #
    # ----------------- #

    form = ItemAdminForm

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def save_model(self, request, obj, form, change):
        """
        Adds onto the basic functionality of saving a submission
        inside the Admin Panel.

        ----

        Adds the ability to upload a raw source thumbnail directly and
        handle automatic file instance creation.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :param obj: The submission instance
        :type obj: submissions.models.Submission

        :param form: The form instance
        :type form: django.forms.ModelForm

        :param change: Whether the form was changed or not
        :type change: bool

        :return: None
        :rtype: None
        """

        thumbnail_source = form.cleaned_data.get("thumbnail_source")

        if thumbnail_source:
            obj.save(thumbnail_source=thumbnail_source)

        super().save_model(request, obj, form, change)
