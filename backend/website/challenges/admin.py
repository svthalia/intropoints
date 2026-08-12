from django import forms
from django.conf import settings
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter

from challenges.models import Challenge, ChallengeQuerySet  # noqa: F401
from submissions.models import Submission

# --------------------------- #
# Custom Challenge Admin Form #
# --------------------------- #


class ChallengeAdminForm(forms.ModelForm):
    """
    Class that represents and extension form for the
    admin panel for Submission Addition.

    ----

    **Contains** the settings:

    - ``thumbnail_source``: The file upload form field
    """

    thumbnail_source = forms.FileField(
        label="Upload a thumbnail (Optional)",
        widget=forms.ClearableFileInput(attrs={"accept": ", ".join(sorted(settings.ALLOWED_MIME_TYPES))}),
        required=False,
    )

    class Meta:
        model = Challenge
        fields = (
            "name",
            "slug",
            "tournament",
            "description",
            "thumbnail_source",
            "enabled",
            "points",
            "active_from",
            "active_until",
            "submission_visibility",
        )


# --------------------- #
# Challenge Admin Panel #
# --------------------- #


@admin.register(Challenge)
class ChallengeAdminPanel(ImportExportModelAdmin):
    """
    Class that represents the admin panel configuration
    for the Challenge model.

    ----

    **Contains** the forms:

    - ``list_display``: The list display fields
    - ``search_fields``: The search fields
    - ``ordering_fields``: The fields that affect ordering
    - ``prepopulated_fields``: The prepopulated slug field
    - ``actions``: The bulk enable/disable actions
    """

    list_display = (
        "name",
        "tournament",
        "active_from",
        "active_until",
        "points",
        "number_of_submissions",
        "enabled",
        "submission_visibility",
    )

    search_fields = ("name", "tournament__name")
    ordering = (
        "-active_from",
        "-active_until",
        "name",
    )

    list_filter = (
        "enabled",
        "tournament",
        ("active_from", DateRangeFilter),
        ("active_until", DateRangeFilter),
        "submission_visibility",
    )

    prepopulated_fields = {"slug": ("name",)}
    actions = ["disable_challenges", "enable_challenges"]

    # ----------- #
    # Custom Form #
    # ----------- #

    form = ChallengeAdminForm

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def save_model(self, request, obj, form, change):
        """
        Overrides the main save functionality in order to pass
        a source file to the challenge ``save(...)`` call.

        ----

        :param request: The HTTP request that was made
        :type request:  django.http.HttpRequest

        :param obj: The challenge instance
        :type obj:  Challenge

        :param form: The admin form
        :type form:  django.forms.ModelForm

        :param change: Whether the model is changed or not
        :type change:  bool

        :return:
        """

        thumbnail_source = form.cleaned_data.get("thumbnail_source")

        if thumbnail_source:
            obj.save(thumbnail_source=thumbnail_source)

    # ----------------------- #
    # Additional form actions #
    # ----------------------- #

    def disable_challenges(self, request, queryset):
        """
        Disables all challenges in the queryset.

        ----

        :param request:  The HTTP request being made
        :type request:  HttpRequest

        :param queryset: The relevant queryset
        :type queryset:  ChallengeQuerySet

        :return: None
        :rtype: None
        """

        self._change_disabled(queryset, True)

    def enable_challenges(self, request, queryset):
        """
        Enables all challenges in the queryset.

        ----

        :param request:  The HTTP request being made
        :type request:  HttpRequest

        :param queryset: The relevant queryset
        :type queryset:  ChallengeQuerySet

        :return: None
        :rtype: None
        """

        self._change_disabled(queryset, False)

    # ----------------- #
    # Additional Fields #
    # ----------------- #

    def number_of_submissions(self, obj):
        """
        Counts the number of submissions for a
        given challenge.

        ----

        :param obj: The challenge instance
        :type obj:  Challenge

        :return: The number of submissions for the challenge
        :rtype:  int
        """

        return Submission.objects.filter(challenge=obj).count()

    def active(self, obj):
        """
        Checks whether a Challenge is currently active.

        ----

        :param obj: The challenge instance
        :type obj:  Challenge

        :return: True if the challenge is active, False otherwise
        :rtype: bool
        """
        return obj.enabled

    # Additional field setup.
    # Somewhat registering base descriptions for them.
    disable_challenges.short_description = "Disable selected challenge"
    enable_challenges.short_description = "Enable selected challenge"
    active.boolean = True

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def _change_disabled(self, queryset, value):
        """
        Sets the disabled field on all challenges in the
        queryset to the given value.

        ----

        :param queryset: The relevant queryset
        :type queryset:  ChallengeQuerySet

        :param value: The new value for the disabled field
        :type value:  bool

        :return: None
        :rtype: None
        """

        queryset.update(disabled=value)
