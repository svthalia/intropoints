from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models.accounts import TeamAccount, TournamentAccount
from teams.models import Team
from tournaments.models import Tournament

User = get_user_model()

# -------------------------------------- #
# Team integrity within tournaments test #
# -------------------------------------- #


class TeamTournamentIntegrityTests(TestCase):
    """
    Tests whether the integrity between ``Teams`` and ``Tournaments``
    is kept all throughout database operations
    """

    def test_one_to_one(self):
        """
        Test to see if the team account side is accessible
        """

        team = Team(name="team")
        team.save()

        account = TeamAccount(name="team_account", team=team)
        account.save()

        self.assertEqual(TeamAccount.objects.get(team=team).name, "team_account")

    def test_one_to_many(self):
        """
        Test to see if the tournament accounts side is accessible as an iterable
        """

        team = Team(name="team")
        team.save()
        tournament = Tournament(name="tournament")
        tournament.save()

        account1 = TournamentAccount(team=team, tournament=tournament, type="coins")
        account2 = TournamentAccount(team=team, tournament=tournament, type="points")

        account1.save()
        account2.save()

        expected_accounts = team.tournament_account.all()

        self.assertIn(account1, expected_accounts)
        self.assertIn(account2, expected_accounts)


# ----------------- #
# Team model basics #
# ----------------- #


class TeamModelTests(TestCase):
    """Tests the Team model representation and relationships."""

    def test_string_representation(self):
        team = Team.objects.create(name="Red Team")
        self.assertEqual(str(team), "Red Team")

    def test_members_relationship(self):
        team = Team.objects.create(name="With Members")
        user = User.objects.create_user(username="member", display_name="Member", initials="ME")

        team.members.add(user)

        self.assertIn(user, team.members.all())
        self.assertIn(team, user.teams.all())

    def test_tournaments_relationship(self):
        team = Team.objects.create(name="With Tournaments")
        tournament = Tournament.objects.create(name="t", slug="t")

        team.tournaments.add(tournament)

        self.assertIn(tournament, team.tournaments.all())
        self.assertIn(team, tournament.teams.all())
