from django.db import models

from accounts.models.transactions import ItemTransaction
from stores.models.items import UsableItem

# -------------- #
# Purchase Model #
# -------------- #


class Purchase(models.Model):
    """
    Class that represents an item store

    ----

    **Contains** the fields:

    - ``team``: The team that made the purchase
    - ``item``: The item the purchase is for
    - ``transaction``: The transaction that made commited the purchase
    - ``created_at``: The date and time the purchase was made
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    team = models.ForeignKey(
        "teams.Team",
        help_text="The team that made the purchase",
        on_delete=models.CASCADE,
        related_name="purchases",
        null=True,
        blank=True,
        default=None,
    )
    """ The team that made the purchase """

    item = models.ForeignKey(
        "stores.Item",
        help_text="The item that the purchase is for",
        on_delete=models.SET_NULL,
        related_name="purchase",
        null=True,
        blank=True,
        default=None,
    )
    """ The bought item """

    transaction = models.OneToOneField(
        "accounts.Transaction",
        help_text="The transaction that committed the purchase",
        on_delete=models.CASCADE,
        related_name="purchase",
        null=True,
        blank=True,
        default=None,
    )
    """ The transaction backend of the purchase """

    created_at = models.DateTimeField(help_text="The time the purchase was made at", null=False, auto_now_add=True)
    """ The time the purchase was made at """

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        ordering = ["-created_at"]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns the string representation of a purchase
        in terms of the team name and the item it wraps around.

        ----

        :param: None

        :return: The string representation of an purchase
        :rtype: str
        """

        return f"{self.team.name} purchased {self.item.name} for {self.item.price}"

    def save(self, *args, **kwargs):
        """
        Overridden in order to commit the purchase to the database
        through a transaction, and to fulfil the purchase by adding
        the item to the team's inventory.

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        # Retrieve the necessary metadata
        tournament = self.item.store.tournament
        account = self.team.get_tournament_coins_account(tournament)

        # Commit the purchase
        self.transaction = ItemTransaction.objects.create(account=account, item=self.item)
        if not self.transaction.accepted:
            raise ValueError("Insufficient funds")

        # Add the purchased item to the team's inventory
        inventory = self.team.get_tournament_inventory(tournament)
        if inventory:
            UsableItem.objects.create(inventory=inventory, item=self.item)

        super().save(*args, **kwargs)
