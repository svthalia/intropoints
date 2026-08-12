from django.db import models

from stores.models.items import UsableItem

# --------------- #
# Inventory Model #
# --------------- #


class Inventory(models.Model):
    """
    Class that represents an item inventory.

    ----

    **Contains** the fields:

    - ``team``: The team it belongs to
    - ``tournament``: The tournament it belongs to
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    tournament = models.ForeignKey(
        "tournaments.Tournament",
        help_text="The tournament this inventory is linked to",
        on_delete=models.CASCADE,
        related_name="inventory",
        null=True,
        blank=False,
        default=None,
    )
    """ The tournament this inventory is linked to """

    team = models.ForeignKey(
        "teams.Team",
        help_text="The team this inventory belongs to",
        on_delete=models.CASCADE,
        related_name="inventory",
        null=True,
        blank=False,
        default=None,
    )
    """ The team this inventory belongs to """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns the string representation of an inventory
        in terms of the tournament it belongs to and its team.

        ----

        :param: None

        :return: The string representation of an inventory
        :rtype: str
        """

        return f"{self.tournament.name} inventory for team {self.team}"

    # --------------------- #
    # Additional Properties #
    # --------------------- #

    @property
    def items(self):
        """
        Retrieves a queryset of all the items
        currently stored in the inventory.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        return UsableItem.objects.filter(inventory=self)
