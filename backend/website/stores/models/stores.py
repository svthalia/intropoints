from django.db import models

# ----------- #
# Store Model #
# ----------- #


class Store(models.Model):
    """
    Class that represents an item store

    ----

    **Contains** the fields:

    - ``tournament``: The tournament it belongs to
    - ``name``: The name of the store
    - ``description``: The description of the store
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    tournament = models.OneToOneField(
        "tournaments.Tournament",
        help_text="The tournament this store belongs to",
        on_delete=models.CASCADE,
        related_name="store",
        null=True,
        blank=False,
        default=None,
    )
    """ The tournament the store belongs to """

    description = models.CharField(
        help_text="The description of the store", max_length=200, null=False, blank=False, default=""
    )
    """ The description of the store """

    name = models.CharField(help_text="The name of the store", max_length=100, null=False, blank=False, default="")
    """ The name of the store """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns the string representation of a store
        in terms of the tournament it belongs to and its name.

        ----

        :param: None

        :return: The string representation of a store
        :rtype: str
        """

        return f"Store: {self.name} for Tournament: {self.tournament.name}"
