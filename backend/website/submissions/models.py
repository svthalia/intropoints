import mimetypes

from django.conf import settings
from django.db import models

from challenges.models import Challenge
from files.models.base import File
from teams.models import Team
from tournaments.models import Tournament

# ----------------- #
# Submission Models #
# ----------------- #


class Submission(models.Model):
    """
    Class that represents a submission to a challenge.

    ----

    **Contains** the fields:

    - ``challenge``: The challenge it belongs to
    - ``tournament`` The tournament the challenge belongs to,
    - ``team` The team it belongs to
    - ``created_by``: The user that created it
    - ``updated_by``: The last user that updated / created it
    - ``created_at``: The time it has been created at
    -  ``file``: The submitted file
    -  ``accepted``: Whether the submission was accepted,
    -  ``is_viewed``: Whether the submission is currently viewed,
    -  ``viewed_at``: The time the submission was last viewed at
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    challenge = models.ForeignKey(
        Challenge,
        help_text="The challenge this submission belongs to",
        on_delete=models.PROTECT,
        related_name="submission",
        null=True,
        blank=False,
        default=None,
    )
    """ The challenge the submission belongs to """

    tournament = models.ForeignKey(
        Tournament,
        help_text="The tournament this submission belongs to",
        on_delete=models.SET_NULL,
        related_name="submission",
        null=True,
        blank=False,
        default=None,
    )
    """ The tournament the submission belongs to """

    team = models.ForeignKey(
        Team,
        help_text="The team this submission belongs to",
        on_delete=models.CASCADE,
        related_name="submission",
        null=True,
        blank=False,
        default=None,
    )
    """ The team the submission belongs to """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="The user who created the submission",
        on_delete=models.SET_NULL,
        related_name="submission_created_by",
        null=True,
        blank=False,
        default=None,
    )
    created_time = models.DateTimeField(auto_now_add=True)
    """ The time the submission was created """

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text="The user who last updated the submission",
        on_delete=models.SET_NULL,
        related_name="submission_updated_by",
        null=True,
        blank=False,
        default=None,
    )
    """ The user that last updated / created the submission """

    file = models.OneToOneField(
        File,
        help_text="The uploaded file for the submission",
        on_delete=models.CASCADE,
        related_name="submission",
        null=True,
        blank=False,
        default=None,
    )
    """ The file that the submission wraps around """

    accepted = models.BooleanField(
        help_text="Whether the submissions was accepted (None = Pending)",
        null=True,
        blank=True,
        default=None,
    )
    """ Whether the submission was accepted or not (None = Pending) """

    received_points = models.IntegerField(
        help_text="The number of points this submission received",
        null=False,
        blank=False,
        default=0,
    )

    is_viewed = models.BooleanField(
        help_text="Whether the submission is viewed",
        null=False,
        blank=False,
        default=False,
    )
    """ Whether the submission is viewed or not """

    viewed_at = models.DateTimeField(
        help_text="The time the submission was viewed at",
        null=True,
        blank=False,
        auto_now_add=True,
    )
    """ The time the submission was last viewed """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the submission to a string object
        based on its team and the challenge it belongs to.

        ----

        :param: None

        :return: The string representation of the submission
        :rtype: str
        """

        return f"Submission by {self.team.name} for the challenge: {self.challenge.name}"

    def save(self, *args, **kwargs):
        """
        Overridden so that the tournament is automatically
        determined by the assigned challenge, and to add the
        possibility to save the model with a file source argument.

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        # Retrieve the tournament
        if self.challenge:
            self.tournament = Tournament.objects.get(id=self.challenge.tournament.id)

        # Try to retrieve the file source if given
        # and initialize the internal file model with
        # the given source
        file_source = kwargs.pop("file_source", None)
        if file_source:
            mime_type = file_source.content_type or mimetypes.guess_type(file_source.name)[0]
            if not mime_type:
                raise ValueError(f"Could not determine MIME type for file: {file_source.name}")

            folder = settings.FILE_STORAGE_SUBMISSIONS_FOLDER
            self.file = File.from_source(file_source, folder)

        return super().save(*args, **kwargs)
