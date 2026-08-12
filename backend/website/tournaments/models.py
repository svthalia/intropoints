from django.db import models
from django.utils import timezone

# -------------------------- #
# Tournament Custom Queryset #
# -------------------------- #


class TournamentQueryset(models.QuerySet):
    """
    Class that represents a custom QuerySet for the
    Challenge model.
    """

    def active(self):
        """
        Filters all active tournaments. Active means the
        current time is between active_from and active_until,
        and the challenge is not disabled.

        ----

        :param: None

        :return: The active set of tournaments
        :rtype: TournamentQueryset
        """

        current_time = timezone.now()
        return self.filter(
            models.Q(active_from__isnull=True) | models.Q(active_from__lte=current_time),
            models.Q(active_until__isnull=True) | models.Q(active_until__gt=current_time),
        )

    def revealed(self):
        """
        Filters all revealed tournaments. Revealed means the current
        time is after active_from and the challenge is not disabled.

        ----

        :param: None

        :return: The revealed set of tournaments
        :rtype: TournamentQueryset
        """

        current_time = timezone.now()
        return self.filter(models.Q(active_from__isnull=True) | models.Q(active_from__lte=current_time))


# ----------------- #
# Tournament Models #
# ----------------- #


class Tournament(models.Model):
    """
    Class that represents a tournament. This is the base of
    the application.

    ----

    The ``Meta`` class **contains** the integrity constraints
    for tournaments.

    ----

    **Contains** the fields:

    - ``name``: The name of the tournament
    - ``slug``: The unique string identifier of the tournament
    - ``active_from``: The time the tournament begins being active
    - ``active_until``: The deadline at which the tournament ends being active
    """

    # --------------- #
    # Database fields #
    # --------------- #

    name = models.CharField(
        help_text="The name of the tournament",
        max_length=100,
        null=False,
        blank=False,
        default="",
    )
    """ The name of the tournament """

    slug = models.SlugField(
        help_text="The unique string identifier of the tournament",
        unique=True,
        null=False,
        blank=False,
        default="",
        max_length=100,
    )
    """ The unique string identifier of the tournament """

    active_from = models.DateTimeField(
        help_text="The time the tournament begins being active",
        null=True,
        blank=False,
        default=None,
    )
    """ The deadline at which the tournament ends being active """

    active_until = models.DateTimeField(
        help_text="The deadline at which the tournament ends being active",
        null=True,
        blank=False,
        default=None,
    )
    """ The deadline at which the tournament ends being active  """

    # -------------- #
    # Custom Manager #
    # -------------- #

    objects = TournamentQueryset.as_manager()

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(active_from__lte=models.F("active_until")),
                name="Tournament start date cannot be after tournament end date",
            ),
        ]
        """
        This constraint makes sure the start time (active_from) is before
        or at the same time as the end time (active_until).
        """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the tournament to a string object
        based on its name.

        ----

        :param: None

        :return: The string representation of the tournament
        :rtype: str
        """

        return f"Tournament {self.name}"

    # --------------------- #
    # Additional Properties #
    # --------------------- #

    @property
    def revealed(self):
        """
        Get whether tournament is revealed. A revealed tournament is
        one whose start date is in the past, it is revealed to the players.

        ----

        :param: None

        :return: ``True`` if it is revealed, ``False`` otherwise
        :rtype: bool
        """

        current_time = timezone.now()
        return self.active_from is None or self.active_from <= current_time

    @property
    def active(self):
        """
        Get whether tournament is active. An active tournament is
        a revealed tournament that hasn't expired yet, ones that
        can still be accessed by players.

        ----

        Note that active tournaments are a subset of revealed tournaments.

        ----

        :param: None

        :return: ``True`` if it is revealed, ``False`` otherwise
        :rtype: bool
        """

        current_time = timezone.now()
        return self.revealed and self.active_until >= current_time
