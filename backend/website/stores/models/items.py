from django.db import models

from files.models.base import File

# ---------- #
# Item Model #
# ---------- #


class Item(models.Model):
    """
    Class that represents a sellable item
    within a store.

    ----

    **Contains** the fields:

    - ``store``: The store it belongs to
    - ``name``: The item's name
    - ``description``: The item's description
    - ``price``: The item's price
    - ``thumbnail``: The optional image of the item
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    store = models.ForeignKey(
        "stores.Store",
        help_text="The store this item belongs to",
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=False,
        default=None,
    )
    """ The store this item belongs to """

    name = models.CharField(
        help_text="The item name",
        max_length=200,
        null=False,
        blank=False,
        default="",
    )
    """ The item's name """

    description = models.TextField(
        help_text="The item's description",
        max_length=400,
        null=False,
        blank=False,
        default="",
    )
    """ The item's description """

    price = models.PositiveIntegerField(
        help_text="The item's price",
        null=False,
        blank=False,
        default=0,
    )

    thumbnail = models.ForeignKey(
        "files.File",
        help_text="The thumbnail image of the item (Optional)",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """ The thumbnail image linked to the item """

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        unique_together = ("store", "name")

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns the string representation of an item
        based on its name.

        ----

        :param: None

        :return: The string representation of an item
        :rtype: str
        """

        return self.name

    def save(self, *args, **kwargs):
        """
        Overridden mainly to be able to create a
        file instance from given raw source file

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        # Try to retrieve a thumbnail
        thumbnail_source = kwargs.pop("thumbnail_source", None)
        if thumbnail_source:
            self.thumbnail = File(source=thumbnail_source)
            self.thumbnail.storage_folder = "items/"
            self.thumbnail.storage_key = f"items/{thumbnail_source.name}"
            self.thumbnail.save()

        super().save(*args, **kwargs)


# ----------------- #
# Usable Item Model #
# ----------------- #


class UsableItem(models.Model):
    """
    Wrapper class that represents a usable
    instance of an already-existing item.

    ----

    **Contains** the fields:

    - ``item``: The wrapped item
    - ``inventory``: The inventory it is stored in
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    item = models.ForeignKey(
        "stores.Item",
        help_text="The base instance of the item",
        on_delete=models.CASCADE,
        related_name="usable_items",
        null=True,
        blank=False,
        default=None,
    )
    """ The base instance of the item """

    inventory = models.ForeignKey(
        "stores.Inventory",
        help_text="The inventory the item belongs to",
        on_delete=models.CASCADE,
        related_name="usable_items",
        null=True,
        blank=False,
        default=None,
    )
    """ The inventory the item belongs to """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns the string representation of a usable
        item based on its linked item name.

        ----

        :param: None

        :return: The string representation of an item
        :rtype: str
        """

        return f"Usable item: {self.item.name}"

    # ------------------------ #
    # Additional Functionality #
    # ------------------------ #

    def use(self):
        """
        Represents the use action of an item.
        When used it deletes the instance and
        creates a proper receipt.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        UsedItemReceipt.objects.create(item=self.item, team=self.inventory.team)
        self.delete()


# ----------------------- #
# Used Item Receipt Model #
# ----------------------- #


class UsedItemReceipt(models.Model):
    """
    Class that represent as successful item use receipt
    that is tracked for action completion.

    ----

    **Contains** the fields:

    - ``item``: The item the receipt is for
    - ``team``: The team that used the item
    - ``used_at``: The time the item was used at
    - ``viewed``: Whether the receipt was inspected by an administrator
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    item = models.ForeignKey(
        "stores.Item",
        help_text="The item the receipt is for",
        on_delete=models.SET_NULL,
        related_name="used_item_receipts",
        null=True,
        blank=False,
        default=None,
    )
    """ The used item the receipt is for """

    team = models.ForeignKey(
        "teams.Team",
        help_text="The team that used the item",
        on_delete=models.CASCADE,
        related_name="used_item_receipts",
        null=True,
        blank=False,
        default=None,
    )
    """ The team that used the item """

    used_at = models.DateTimeField(help_text="The time the item was used at", null=False, auto_now_add=True)
    """ The time the item was used at """

    viewed = models.BooleanField(help_text="Whether the receipt was inspected", null=False, blank=False, default=False)
    """ Whether the receipt was inspected by an administrator"""

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns the string representation of a usable
        item based on its linked item name and team name.

        ----

        :param: None

        :return: The string representation of a receipt
        :rtype: str
        """

        return f"Item {self.item.name} used at {self.used_at}"
