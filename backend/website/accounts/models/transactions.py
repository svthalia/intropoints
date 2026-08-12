from django.db import models, transaction
from django.utils import timezone

# ---------------------- #
# Base Transaction Model #
# ---------------------- #


class Transaction(models.Model):
    """
    Model that handles a currency transaction - regardless
    of the given currency. It must be tied to an account in
    order to function properly, as the balance is stored inside
    the account.

    ----

    **SHOULD** be overridden in order to represent the desired transaction
    type. The method that allows for virtual implementation is:

    - ``self._retrieve_amount(...)``: Choose how the amount is truly retrieved

    ----

    **Contains** the fields:

    - ``account``: The linked account
    - ``amount``: The amount that is added (+) / subtracted (-) from the balance
    - ``accepted``: Whether the transaction was accepted or rejected
    - ``requested_at``: The date at which the transaction was requested
    """

    account = models.ForeignKey(
        # Avoids import circularity.
        # !! Not the most elegant solution !!
        "accounts.Account",
        help_text="The linked account",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        default=None,
        related_name="transactions",
    )
    """ The account towards which the transaction applies """

    amount = models.IntegerField(help_text="The amount the transaction applies", null=True, blank=False, default=0)
    """ The amount the transaction is for """

    accepted = models.BooleanField(
        help_text="Whether the transaction was accepted or rejected", null=False, blank=False, default=False
    )
    """ Whether the transaction was accepted or not """

    requested_at = models.DateTimeField(
        help_text="The time the transaction was requested at", null=False, blank=False, default=timezone.now
    )
    """ The time the transaction was requested at """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Simply returns a base string representation of the transaction.

        ----

        **Since django is treating inheritance in a really weird format**,
        I need to perform down casting here in order to retrieve the
        proper name for some reason. This is really frustrating.

        ----

        :param: None

        :return: The string representation of the transaction
        :rtype: str
        """

        if hasattr(self, "itemtransaction"):
            return self.itemtransaction.__str__()
        if hasattr(self, "admintransaction"):
            return self.admintransaction.__str__()
        if hasattr(self, "reversedtransaction"):
            return self.reversedtransaction.__str__()
        if hasattr(self, "gradingtransaction"):
            return self.gradingtransaction.__str__()
        return "Transaction"

    def save(self, *args, **kwargs):
        """
        Overrides the base save functionality in order
        to atomically commit the transaction to the
        linked account.

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        # Ensure that committing and saving happen together,
        # otherwise the account balance might get updated without
        # the transaction being saved.
        with transaction.atomic():
            # Abstract endpoint for allowing custom amount
            # retrieval
            self._retrieve_amount()
            # Commit the transaction to the linked account
            self.accepted = self._commit()

            # Save the object
            return super().save(*args, **kwargs)

    # ------------------------ #
    # Additional Functionality #
    # ------------------------ #

    def reverse(self):
        """
        Asks the linked account to reverse this transaction.
        If the transaction is not accepted, then this method has\
        no effect.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        # Only reverse accepted transactions
        if not self.accepted:
            return

        self.account.reverse_transaction(self.id)

    # --------------------------- #
    # Extended Base Functionality #
    # --------------------------- #

    def _commit(self):
        """
        Commits the transaction to the linked account.
        If the balance is too low, the transaction is not
        commited to the account and marked as rejected.

        ----

        :param: None

        :return: Whether the transaction succeeded
        :rtype: bool
        """

        # If the amount is negative, safely subtract from the balance
        if self.amount < 0:
            res = self.account.subtract_from_balance(abs(self.amount))
        # Otherwise add it to the balance
        else:
            res = self.account.add_to_balance(self.amount)

        return res == self.account.BALANCE_UPDATED

    # ------------------- #
    # Abstract Components #
    # ------------------- #

    def _retrieve_amount(self):
        """
        **!! Virtual method, implement it in subclass !!**

        ----

        Overrides the amount for the transaction by allowing
        for custom retrieval. The method should not return anything.
        Rather change the amount for the object.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        return


# -------------------------- #
# Reverted Transaction Model #
# -------------------------- #


class ReversedTransaction(Transaction):
    """
    Transaction model that simply represents a previous
    transaction that has been reverted.

    ----

    **Adds** the fields:

    - ``transaction``: A link to the reverted transaction
    """

    transaction = models.ForeignKey(
        Transaction, on_delete=models.PROTECT, null=False, blank=False, related_name="reversed_transactions"
    )

    # ------------ #
    # Base methods #
    # ------------ #

    def __str__(self):
        """
        Returns a string representation based on the
        reversed transaction.

        ----

        :param: None

        :return: The string representation of the transaction
        :rtype: str
        """

        return f'Reversed transaction "{self.transaction.__str__()}"'


# ---------------------- #
# Item Transaction Model #
# ---------------------- #


class ItemTransaction(Transaction):
    """
    Transaction model that handles Item transactions.
    The amount is automatically determined based on the
    item price.

    ----

    **Adds** the fields:

    - ``transaction``: A link to the item that is bought
    """

    item = models.ForeignKey(
        "stores.Item",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="transactions",
    )

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns a string representation based on the item for
        which the transaction will be made for.

        ----

        :param: None

        :return: The string representation of the transaction
        :rtype: str
        """

        return f"Item transaction: For {self.item.__str__()}"

    # ------------------------ #
    # Overridden Functionality #
    # ------------------------ #

    def _retrieve_amount(self):
        """
        Overrides the transaction amount to that of
        the item price.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        self.amount = -self.item.price
        return


# ------------------------- #
# Grading Transaction Model #
# ------------------------- #


class GradingTransaction(Transaction):
    """
    Transaction model that represents the transaction
    for points after a submission has been graded.

    Links a transaction to a given submission.

    ----

    **Adds** the fields:

    - ``transaction``: A link to the submission that caused it
    """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns a string representation grading transaction based
        on the amount of points awarded or removed.

        ----

        :param: None

        :return: The string representation of the transaction
        :rtype: str
        """

        action_str = "Subtracting" if self.amount < 0 else "Adding"

        return f"Grading Transaction: {action_str}  {abs(self.amount)}"

    # ------------------------ #
    # Overridden functionality #
    # ------------------------ #

    def _retrieve_amount(self):
        """
        Since grading can subtract team points, this
        means that if too many points are subtracted, the
        account balance should be set to 0.

        Hence, to make the commit pass, if the balance is too
        low for the transaction to pass, the transaction amount is
        set precisely to that of the balance.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        # Checking if the transaction amount exceeds the
        # account balance. If so, cap it to the account balance.
        if self.amount < 0:
            self.amount = self.amount if self.account.balance > abs(self.amount) else -self.account.balance

        return


# ----------------------- #
# Admin Transaction Model #
# ----------------------- #


class AdminTransaction(Transaction):
    """
    Special transaction model extension that handles
    Administrator only changes.

    ----

    Allows for arbitrary transactions. This means that it should
    only be used in special cases.
    """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Returns a string representation of the special transaction
        based on the result that the transaction will have.

        ----

        :param: None

        :return: The string representation of the transaction
        :rtype: str
        """

        action_str = "Subtracting" if self.amount < 0 else "Adding"

        return f"Administrator Transaction: {action_str}  {abs(self.amount)}"

    # ------------------------ #
    # Overridden functionality #
    # ------------------------ #

    def _retrieve_amount(self):
        """
        An administrator transaction should pass no matter what.
        Since it was it the requirements after all.

        Hence, to make the commit pass, if the balance is too
        low for the transaction to pass, the transaction amount is
        set precisely to that of the balance.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        # Checking if the transaction amount exceeds the
        # account balance. If so, cap it to the account balance.
        if self.amount < 0:
            self.amount = self.amount if self.account.balance > abs(self.amount) else -self.account.balance

        return
