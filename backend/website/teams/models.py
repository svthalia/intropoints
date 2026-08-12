from django.db import models

from accounts.models.accounts import TeamAccount, TournamentAccount
from accounts.models.transactions import GradingTransaction
from stores.models.inventories import Inventory
from tournaments.models import Tournament
from users.models import User

# ----------- #
# Team Models #
# ----------- #


class Team(models.Model):
    """
    Class that represents a team of application users.
    Users by themselves cannot enter in actives, yet
    teams can.

    ----

    **Contains** the fields:

    - ``name``: The name of the team
    - ``tournaments``: The tournaments that the team has joined
    - ``members``: The users of the team
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    name = models.CharField(
        help_text="The name of the team",
        max_length=100,
        null=False,
        blank=False,
        default="",
    )
    """ The name of the team """

    tournaments = models.ManyToManyField(
        Tournament,
        help_text="The tournaments that the team has joined",
        related_name="teams",
        blank=True,
        default=None,
    )
    """ The tournaments that the team has joined """

    members = models.ManyToManyField(
        User, help_text="The users of the team", related_name="teams", blank=True, default=None
    )
    """ The users within the team """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Convert this object to a string representation
        based on its name.

        ----

        :param: None

        :return: A string representation of this object
        :rtype: str
        """

        return f"{self.name}"

    def save(self, *args, **kwargs):
        """
        Overrides the base save functionality such that
        point accounts are generated and set for a team on
        creation.

        ----

        :param args: Positional arguments
        :type args: dict

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return:
        """

        super().save(*args, **kwargs)

    # ------------------------ #
    # Additional Functionality #
    # ------------------------ #

    def get_main_account(self):
        """
        Retrieve the main points account for
        the team

        ----

        :param: None

        :return: The account instance
        :rtype: accounts.models.accounts.Account
        """

        return TeamAccount.objects.get(team=self)

    def get_tournament_coins_account(self, tournament):
        """
        Retrieve the account that stores the spendable coins
        for the team for the given tournament.

        ----

        :param tournament: The inspected tournament
        :type tournament: Tournament

        :return: The coins account
        :rtype: accounts.models.accounts.Account
        """

        return TournamentAccount.objects.get(team=self, tournament=tournament, type="coins")

    def get_tournament_points_account(self, tournament):
        """
        Retrieve the account that stores the points
        for the team for the given tournament.

        ----

        :param tournament: The inspected tournament
        :type tournament: Tournament

        :return: The coins account
        :rtype: accounts.models.accounts.Account
        """

        return TournamentAccount.objects.get(team=self, tournament=tournament, type="points")

    def get_tournament_inventory(self, tournament):
        """
        Retrieves the team's current tournament usable
        item inventory.

        ---

        :param tournament: The inspected tournament
        :type tournament: Tournament

        :return: The inventory
        :rtype: stores.models.inventories.Inventory
        """

        return Inventory.objects.get(team=self, tournament=tournament)

    def grade(self, tournament, amount):
        """
        Gives or takes points and coins to the
        team respectively.

        Utility for keeping track of both the individual and
        global account.

        ----

        :param tournament: The tournament for which the submission is for
        :type tournament: Tournament

        :param amount: The amount of currency
        :type amount: int

        :return: None
        :rtype: None
        """

        tournament_points_account = self.get_tournament_points_account(tournament)
        tournament_coins_account = self.get_tournament_coins_account(tournament)
        main_points_account = self.get_main_account()

        GradingTransaction.objects.create(account=tournament_points_account, amount=amount)
        GradingTransaction.objects.create(account=tournament_coins_account, amount=amount)
        GradingTransaction.objects.create(account=main_points_account, amount=amount)

        return
