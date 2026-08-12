from django.db import models, transaction

from accounts.models.transactions import ReversedTransaction, Transaction

# ----------------------- #
# Custom Account QuerySet #
# ----------------------- #


class AccountQueryset(models.QuerySet):
    """
    Queryset that allows for specific account type
    retrievals.
    """

    # ------------------------ #
    # Additional Functionality #
    # ------------------------ #

    def points(self):
        """
        Retrieves the points accounts.

        ----

        :params: None

        :return: The accounts with their type being ``points``
        :rtype: AccountQueryset
        """

        return self.filter(type="points")

    def coins(self):
        """
        Retrieves the coins accounts.

        ----

        :params: None

        :return: The accounts with their type being ``coins``
        :rtype: AccountQueryset
        """

        return self.filter(type="coins")


# -------------- #
# Account Models #
# -------------- #


class Account(models.Model):
    """
    Model that handles any type of account, regardless of
    currency.

    ----

    **MAY** be used as a base class to extend functionality,
    by including extra fields; do not override any other functionality!

    ----

    **Provides** the constants:

    - ``BALANCE_UPDATED``: Represents that the balance was just updated
    - ``BALANCE_TOO_LOW``: Represents that the balance was not updated because of funds

    ----

    **Contains** the fields:

    - ``balance``: The account's balance
    """

    # Static enum types for balance notifications.
    # Can be extended if needed.
    BALANCE_UPDATED = 0
    BALANCE_TOO_LOW = 1

    balance = models.PositiveIntegerField(help_text="The account's balance", null=False, blank=False, default=0)
    """ The account's current balance """

    name = models.CharField(help_text="The account's name", max_length=255, null=False, blank=False, default="")
    """ The name of the account """

    # ------------ #
    # Base methods #
    # ------------ #

    def __str__(self):
        """
        Returns the string representation of the Account in
        terms of its name.

        ----

        :params: None

        :return: The string representation of the Account
        :rtype: str
        """

        return f"Account: {self.name}"

    # ------------------------ #
    # Additional functionality #
    # ------------------------ #

    def reverse_transaction(self, transaction_id):
        """
        Reverses the transaction with the given id by creating a
        counter-transaction for the Account.

        ----

        :params transaction_id: The id of the transaction to be reversed;
        :type transaction_id: int

        :return: None
        :rtype: None
        """

        # Ensure that the operation is atomic so that it
        # cannot cause threading issues
        with transaction.atomic():
            # Retrieve the old transaction
            last_transaction = Transaction.objects.get(id=transaction_id)

            # Create its counterpart and save it
            reversed_transaction = ReversedTransaction.objects.create(
                account=self, amount=-last_transaction.amount, transaction=last_transaction
            )
            reversed_transaction.save()

    def add_to_balance(self, amount):
        """
        Adds the given amount atomically to the account
        balance and updates it.

        As of now, this operation has **NO** reason to fail.

        ----

        :param amount: The amount to be added to the balance
        :type amount: int

        :return: BALANCE_TOO_LOW | BALANCE_UPDATED
        :rtype: int
        """

        with transaction.atomic():
            # Locks the given account in order to commit the
            # transaction value.
            account = Account.objects.select_for_update().get(pk=self.pk)
            account.balance += amount
            account.save()
            self.refresh_from_db()

            return Account.BALANCE_UPDATED

    def subtract_from_balance(self, amount):
        """
        Tries to subtract the given amount safely from the
        account balance and updates it.

        If the balance is too low, the transaction is refused.

        ----

        :param amount: The amount to be added to the balance
        :type amount: int

        :return: BALANCE_TOO_LOW | BALANCE_UPDATED
        :rtype: int
        """

        with transaction.atomic():
            # Get the account lock
            account = Account.objects.select_for_update().get(pk=self.pk)

            # Only commit to the account if the
            # balance is high enough
            if account.balance < amount:
                return Account.BALANCE_TOO_LOW

            account.balance -= amount
            account.save()
            self.refresh_from_db()

            return Account.BALANCE_UPDATED


# ------------------------ #
# Tournament Account Model #
# ------------------------ #


class TournamentAccount(Account):
    """
    Model that is simply wrapping around the base
    Account class, in order to specify it as account
    exclusive to tournaments and to link it to both a
    team and a tournament.

    ----

    **Adds** the fields:

    - ``team``: The linked team
    - ``tournament``: The linked tournament
    - ``type``: The type of the account
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    team = models.ForeignKey(
        "teams.Team",
        help_text="The linked team to the account",
        on_delete=models.SET_NULL,
        related_name="tournament_account",
        null=True,
        blank=False,
        default=None,
    )
    """ The linked team to the account """

    tournament = models.ForeignKey(
        "tournaments.Tournament",
        help_text="The linked tournament to the account",
        on_delete=models.SET_NULL,
        related_name="tournament_account",
        null=True,
        blank=False,
        default=None,
    )
    """ The linked tournament to the account """

    type = models.CharField(
        help_text="The type of the account",
        max_length=10,
        choices=[("points", "points"), ("coins", "coins")],
        null=False,
        blank=False,
        default="points",
    )
    """ The currency type of the account """

    # -------------- #
    # Custom Manager #
    # -------------- #

    objects = AccountQueryset.as_manager()

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "tournament", "type"], name="One account for each tournament of each team of each type"
            )
        ]


# ------------------ #
# Team Account Model #
# ------------------ #


class TeamAccount(Account):
    """
    Model that is simply wrapping around the base
    Account class, in order to specify it as a point
    account that keeps track of all the tournament points

    ----

    **Adds** the fields:

    - ``team``: The linked team
    """

    team = models.ForeignKey(
        "teams.Team",
        help_text="The linked team to the account",
        on_delete=models.SET_NULL,
        related_name="team_account",
        null=True,
        blank=False,
        default=None,
    )
