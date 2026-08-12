from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models.accounts import Account, TournamentAccount
from accounts.models.transactions import Transaction
from challenges.models import Challenge, ChallengeUtils
from stores.models.items import Item
from stores.models.purchases import Purchase
from stores.models.stores import Store
from submissions.models import Submission
from teams.models import Team
from tournaments.models import Tournament

# ----------------------- #
# Base test model Factory #
# ----------------------- #


# In order to standardize instance creation over all,
# tests, it's better to use a Factory class that does so.
#
# If any other utilities need to be made. Include them here.


class TestFactoryUtils:
    """
    Base factory class that can create all the necessary
    models in order to test the application.

    ----

    **Factories** can skip saving with:

    - ``save=False``

    ----

    **Provides** factories for:

    - ``make_user(...)``: User

    - ``make_tournament(...)``: Tournament
    - ``make_challenge(...)``: Challenge

    - ``make_transaction(...)``: Transaction

    - ``make_account(...)``: Account
    - ``make_tournament_account(...)``: TournamentAccount

    - ``make_team(...)``: Team
    - ``make_submission(...)``: Submission

    - ``make_purchase(...)``: Purchase
    - ``make_store(...)``: Store
    - ``make_item(...)``: Item
    """

    # ----------- #
    # User models #
    # ----------- #

    def make_user(self, name="Test User"):
        """
        Creates an unsaved User instance.
        This is unique no matter what name is given.

        ----

        :param name: The username
        :type name: str

        :return: The unsaved user instance
        :rtype: users.models.User
        """

        get_user_model().objects.create(username=name, display_name=name, initials=name[:-1])

    # ----------------- #
    # Tournament models #
    # ----------------- #

    @staticmethod
    def make_tournament(**kwargs):
        """
        Creates an unsaved Tournament instance.
        You can pass the same arguments you would pass
        to a Tournament.

        ----

        :param kwargs: The dictionary of tournament arguments
        :type kwargs: dict

        :return: The tournament instance
        :rtype: Tournament
        """

        tournament = Tournament(
            name=kwargs.get("name", "Test Tournament"),
            slug=kwargs.get("slug", "test-tournament"),
            active_from=kwargs.get("active_from", timezone.now()),
            active_until=kwargs.get("active_until", timezone.now() + timedelta(hours=1)),
        )

        if not kwargs.get("save"):
            return tournament

        tournament.save()
        return tournament

    # ---------------- #
    # Challenge models #
    # ---------------- #

    @staticmethod
    def make_challenge(**kwargs):
        """
        Creates an unsaved Challenge instance.
        Pass the same arguments you would pass
        to a Challenge.

        ----

        **Pass** the custom tournament via:

        - ``tournament=``

        ----



        ----

        :param kwargs: The dictionary of challenge arguments
        :type kwargs: dict

        :return: The challenge instance
        :rtype: Challenge
        """

        challenge = Challenge(
            name=kwargs.get("name", "Test Challenge"),
            tournament=kwargs.get("tournament", TestFactoryUtils.make_tournament()),
            slug=kwargs.get("slug", "test-challenge"),
            description=kwargs.get("description", "A test challenge."),
            points=kwargs.get("points", 10),
            enabled=kwargs.get("enabled", True),
            active_from=kwargs.get("active_from"),
            active_until=kwargs.get("active_until"),
            submission_visibility=kwargs.get("submission_visibility", ChallengeUtils.SUBMISSIONS_ALWAYS_VISIBLE),
        )

        if not kwargs.get("save"):
            return challenge

        challenge.save()
        return challenge

    # ------------------ #
    # Transaction models #
    # ------------------ #

    @staticmethod
    def make_transaction(account, amount=0, description="NOP", **kwargs):
        """
        Generates a transaction instance with the given parameters,
        or defaults to the default ones.

        ----

        :param account: The linked account to the transaction
        :type account: Account

        :param amount: The amount the transaction is for
        :type amount: int

        :param description: The description of the transaction
        :type description: str

        :return: The transaction instance
        :rtype: Transaction
        """

        transaction = Transaction.objects.create(
            account=account,
            amount=amount,
            description=description,
        )

        if not kwargs.get("save"):
            return transaction

        transaction.save()
        return transaction

    @staticmethod
    def make_account(name="Test Account", **kwargs):
        """
        Creates an account instance with either the
        default parameters, or the given ones.

        ----

        :param name: The name of the account
        :type name: str

        :return: The unsaved account instance
        :rtype: Account
        """

        account = Account(name=name)

        if not kwargs.get("save"):
            return account

        account.save()
        return account

    @staticmethod
    def make_tournament_account(team, tournament, **kwargs):
        """
        Creates a tournament account instance with
        either the default parameters, or the given ones.

        ----

        :param team: The given team
        :type team: Team

        :param tournament: The given tournament
        :type tournament: Tournament

        :return: The unsaved tournament account instance
        :rtype: TournamentAccount
        """

        if not tournament:
            tournament = TestFactoryUtils.make_tournament()

        if not team:
            team = TestFactoryUtils.make_team()

        tournament_account = TournamentAccount(tournament=tournament, team=team)

        if not kwargs.get("save"):
            return tournament_account

        tournament_account.save()
        return tournament_account

    # ----------- #
    # Team models #
    # ----------- #

    @staticmethod
    def make_team(tournaments, member_count=1, name="Test Team", **kwargs):
        """
        Creates a team instance with either the
        default parameters, or the given ones.

        ----

        :param tournaments: The tournaments that the user should join
        :type tournaments: TournamentQueryset

        :param member_count: How many test members should be added
        :type member_count: int

        :param name: The name of the team
        :type name: str

        :return: The unsaved team instance
        :rtype: Team
        """

        # If not tournaments were given, use
        # a single one
        if not tournaments:
            tournaments = Tournament.objects.none()
            tournaments |= TestFactoryUtils.make_tournament()

        # Create the team and add the specified
        # number of users
        team = Team(name=name)
        for _i in range(member_count):
            member = TestFactoryUtils.make_user()
            team.members.add(member)

        # Add the tournaments the team should
        # be joining
        for tournament in tournaments:
            team.tournaments.add(tournament)

        if not kwargs.get("save"):
            return team

        team.save()
        return team

    # ----------------- #
    # Submission models #
    # ----------------- #

    @staticmethod
    def make_submission(**kwargs):
        """
        Creates an unsaved Submission instance.
        You can the same arguments you would pass
        to a Submission.

        ----

        **Pass** the custom challenge via:

        - ``challenge``

        **Pass** the custom team via:

        - ``team``

        ----

        :param kwargs: The dictionary of submission arguments
        :type kwargs: dict

        :return: The unsaved submission instance
        :rtype: Submission
        """

        submission = Submission(
            team=kwargs.get("team", TestFactoryUtils.make_team()),
            challenge=kwargs.get("challenge", TestFactoryUtils.make_challenge()),
            accepted=kwargs.get("accepted", True),
        )

        if not kwargs.get("save"):
            return submission

        submission.save()
        return submission

    # ------------ #
    # Store models #
    # ------------ #

    @staticmethod
    def make_store(tournament=None, **kwargs):
        """
        Creates an unsaved store instance
        for testing.

        ----

        :param tournament: The optional tournament
        :type tournament: Tournament

        :return: The unsaved store instance
        :rtype: Store
        """

        if tournament is None:
            tournament = TestFactoryUtils.make_tournament()
            tournament.save()

        store = Store(
            tournament=tournament,
            description="Test store",
        )

        if not kwargs.get("save"):
            return store

        store.save()
        return store

    @staticmethod
    def make_item(store=None, **kwargs):
        """
        Creates an unsaved item instance
        for testing.

        ----

        :param store: The optional store
        :type store: Store

        :return: The unsaved store instance
        :rtype: Store
        """

        if not store:
            store = TestFactoryUtils.make_store()

        item = Item(
            store=store,
            name=kwargs.get("name", "Test Item"),
            description=kwargs.get("description", "A test item"),
            price=kwargs.get("price", 100),
            thumbnail=kwargs.get("thumbnail"),
        )

        if not kwargs.get("save"):
            return item

        item.save()
        return item

    @staticmethod
    def make_purchase(team=None, item=None, **kwargs):
        """
        Creates an unsaved purchase instance
        for testing.

        ----

        :param team: The optional team
        :type team: Team

        :param item: The optional item
        :type item: Item

        :return: The unsaved purchase instance
        :rtype: Purchase
        """

        if team is None:
            team = TestFactoryUtils.make_team()

        team_account = TestFactoryUtils.make_tournament_account(team=team)
        TestFactoryUtils.make_transaction(amount=200, account=team_account)

        if item is None:
            item = TestFactoryUtils.make_item()

        purchase = Purchase(
            team=team,
            item=item,
        )

        if not kwargs.get("save"):
            return purchase

        purchase.save()
        return purchase
