from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin, messages
from django.http import HttpRequest  # noqa: F401

from submissions.models import Submission

# ---------------------- #
# Submission Admin Panel #
# ---------------------- #


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """
    Class that represents the admin panel configuration for the
    Submission model. Customizes the creation of submissions, and
    their retrieval.

    ----

    **Contains** the fields:

    - ``fields``: The editable fields
    - ``readonly_fields``: The readonly fields
    - ``list_display``: The fields displayed on the list view
    - ``ordering``: The ordering for files
    - ``list_filter``: The filter forms that can be used for the list view
    """

    fields = (
        "challenge",
        "team",
        "file",
        "accepted",
    )

    readonly_fields = fields

    list_display = (
        "id",
        "team",
        "challenge",
        "tournament",
        "created_by",
        "updated_by",
        "accepted",
    )

    ordering = ("-created_by",)

    list_filter = (
        ("team", AutocompleteListFilter),
        ("challenge", AutocompleteListFilter),
        ("tournament", AutocompleteListFilter),
        "accepted",
    )

    # ------------------ #
    # Base functionality #
    # ------------------ #

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """
        Displays a warning when opening a submission if the team already has
        an accepted submission for the same challenge.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param object_id: The submission's id
        :type object_id: int

        :param form_url: The currently viewed form URL
        :type form_url: str

        :param extra_context: Dictionary arguments
        :type extra_context: dict

        :return: None
        :rtype: None
        """

        # Check if the objects exists
        if object_id:
            obj = self.get_object(request, object_id)

            # Check whether the submission already exists
            if (
                Submission.objects.filter(challenge=obj.challenge, team=obj.team, accepted=True)
                .exclude(pk=obj.pk)
                .exists()
            ):
                # Warn the user
                self.message_user(
                    request,
                    "This team already has an accepted Submission for this Challenge.",
                    level=messages.WARNING,
                )

        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Adds onto the basic functionality of saving a submission
        inside the Admin Panel.

        ----

        Assigns the user that creates it / updates it.

        ----

        Adds the ability to upload a raw source file directly and
        handle automatic file instance creation.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param obj: The submission instance
        :type obj: Submission

        :param form: The currently viewed form
        :type form: SubmissionCustomForm

        :param change: Whether the model is updated or created
        :type change: bool

        :return: None
        :rtype: None
        """

        file_source = form.cleaned_data.get("file_source")

        if file_source:
            obj.save(file_source=file_source)

        # Check if the model is being created or
        # changed / updated
        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """
        Submissions should only be handled through the right
        frontend flow.

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
        Submissions should only be handled through the right
        frontend flow.

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
