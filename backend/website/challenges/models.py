from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from files.models.base import File
from tournaments.models import Tournament

# ------------------------- #
# Challenge Custom Queryset #
# ------------------------- #


class ChallengeQuerySet(models.QuerySet):
    """
    Class that represents a custom QuerySet for the
    Challenge model.
    """

    def active(self):
        """
        Filters all active challenges. Active means the
        current time is between active_from and active_until,
        and the challenge is not disabled.

        ----

        :param: None

        :return: The active set of challenges
        :rtype: ChallengeQuerySet
        """

        # Filter for challenges that are NOT disabled
        # AND their `active_from` date is valid AND
        # their `active_until` date is valid
        current_time = timezone.localtime()
        return self.filter(
            Q(enabled=True),
            Q(active_from=None) | Q(active_from__lte=current_time),
            Q(active_until=None) | Q(active_until__gt=current_time),
        )

    def revealed(self):
        """
        Filters all revealed challenges. Revealed means the current
        time is after active_from and the challenge is not disabled.

        ----

        :param: None

        :return: The revealed set of challenges
        :rtype: ChallengeQuerySet
        """

        # Filter for challenges that are NOT disabled
        # and their `active_from` date is valid.
        current_time = timezone.localtime()
        return self.filter(Q(enabled=True) & (Q(active_from=None) | Q(active_from__lte=current_time)))


# --------------- #
# Challenge Utils #
# --------------- #


class ChallengeUtils:
    """
    Class that provides basic utilities for challenges.

    ----

    **Provides** visibility settings:

    - ``SUBMISSIONS_ALWAYS_VISIBLE``
    - ``SUBMISSIONS_VISIBLE_ON_ACCEPTED``

    ----

    **Provides** the set of visibility settings:

    - ``SUBMISSION_VISIBILITY_CHOICES``
    """

    SUBMISSIONS_ALWAYS_VISIBLE = 1
    """ Submission are always visible """
    SUBMISSIONS_VISIBLE_ON_ACCEPTED = 2
    """ Submission are only visible when accepted """

    SUBMISSION_VISIBILITY_CHOICES = [
        (SUBMISSIONS_ALWAYS_VISIBLE, "Always visible"),
        (SUBMISSIONS_VISIBLE_ON_ACCEPTED, "When accepted"),
    ]
    """ Submission visibility set """


# ---------------- #
# Challenge Models #
# ---------------- #


class Challenge(models.Model):
    """
    Class that represents a challenge. Used in Tournaments.

    ----

    **Contains** the fields:

    - ``name``: The challenge name
    - ``description``: The challenge description
    - ``tournament``: The tournament it belongs to
    - ``slug``: The challenge's string identifier
    - ``thumbnail``: The challenge's optional image
    - ``active_from``: The start time
    - ``active_until``: The end deadline
    - ``points``: The points awarded when completed
    - ``submission_visibility``: The submission visibility settings
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    name = models.CharField(help_text="The challenge's title", max_length=80, null=False, blank=False, default="")
    """ The challenge's name """

    tournament = models.ForeignKey(
        Tournament,
        help_text="The tournament to which the challenge belongs to",
        related_name="challenge",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )
    """ The tournament the challenge belongs to """

    slug = models.SlugField(
        help_text="URL-friendly shorthand identifier for the challenge",
        max_length=80,
        unique=True,
    )
    """ The string identifier for the challenge """

    description = models.TextField()
    """ The challenge's description """

    thumbnail = models.ForeignKey(
        "files.File",
        help_text="The challenge's thumbnail",
        on_delete=models.SET_NULL,
        related_name="challenge",
        null=True,
        blank=True,
        default=None,
    )
    """ The challenges display thumbnail (Optional) """

    enabled = models.BooleanField(
        help_text="Whether the challenge is visible to users. Enabled by default",
        null=False,
        blank=False,
        default=True,
    )
    """ Whether the challenge is enabled or not """

    active_from = models.DateTimeField(
        help_text="When the challenge becomes active. Leave empty for no start restriction",
        null=True,
        blank=True,
        default=None,
    )
    """ The time the challenge becomes active from """

    active_until = models.DateTimeField(
        help_text="When the challenge stops being active. Leave empty for no end restriction",
        null=True,
        blank=True,
        default=None,
    )
    """ The time the challenge becomes inactive from """

    points = models.PositiveIntegerField(
        help_text="The amounts of points awarded",
        null=False,
        blank=False,
        default=0,
    )
    """ The number of points awarded for completing the challenge """

    submission_visibility = models.PositiveIntegerField(
        help_text="When and how the submissions should be visible to the users",
        choices=ChallengeUtils.SUBMISSION_VISIBILITY_CHOICES,
        default=ChallengeUtils.SUBMISSIONS_ALWAYS_VISIBLE,
    )
    """ When the submission option should be visible to the users """

    # -------------- #
    # Custom Manager #
    # -------------- #

    objects = ChallengeQuerySet.as_manager()

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self) -> str:
        """
        Converts the challenge to a string object
        based on its name.

        ----

        :param: None

        :return: The challenge string identifier
        :rtype: str
        """

        return f"{self.name} challenge"

    def save(self, *args, **kwargs):
        """
        Overridden in order to save a thumbnail
        from a given source file.

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        thumbnail_source = kwargs.pop("thumbnail_source", None)
        if thumbnail_source:
            self.thumbnail = File.from_source(
                source=thumbnail_source, storage_folder=settings.FILE_STORAGE_CHALLENGES_FOLDER
            )

        super().save(*args, **kwargs)

    # --------------------- #
    # Additional properties #
    # --------------------- #

    @property
    def is_revealed(self):
        """
        Checks whether a Challenge is currently revealed.
        Revealed means the challenge is enabled, the tournament
        is revealed,  and the current time is after active_from.

        ----

        :param: None

        :return: ``True`` if it is revealed, ``False`` otherwise
        :rtype: bool
        """

        # No challenge can be active if
        # it's not enabled
        if not self.enabled:
            return False

        if not self.tournament.revealed:
            return False

        current_time = timezone.localtime()
        return self.active_from is None or self.active_from <= current_time

    @property
    def is_active(self):
        """
        Checks whether a Challenge is currently active.
        Active means the challenge is enabled and the current
        time is within the active_from and active_until window.

        ----

        :param: None

        :return: ``True`` if the challenge is active, ``False`` otherwise
        :rtype: bool
        """

        # No challenge can be active if
        # it's not enabled
        if not self.enabled:
            return False

        current_time = timezone.localtime()
        return self.is_revealed and (self.active_until is None or self.active_until >= current_time)
