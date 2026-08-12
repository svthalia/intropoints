from datetime import timedelta

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from challenges.models import Challenge
from core.tests.utils import TestFactoryUtils
from tournaments.models import Tournament


def make_tournament(revealed=True):
    """Creates a saved tournament that is revealed (or not)."""
    now = timezone.now()
    return Tournament.objects.create(
        name="t",
        slug="t",
        active_from=now - timedelta(hours=1) if revealed else now + timedelta(hours=1),
        active_until=now + timedelta(hours=2),
    )


def make_saved_challenge(tournament=None, **kwargs):
    """Creates a saved challenge for queryset/constraint tests."""
    if tournament is None:
        tournament = make_tournament()
    return Challenge.objects.create(
        name=kwargs.get("name", "Test Challenge"),
        slug=kwargs.get("slug", "test-challenge"),
        description=kwargs.get("description", "A test challenge."),
        tournament=tournament,
        points=kwargs.get("points", 10),
        enabled=kwargs.get("enabled", True),
        active_from=kwargs.get("active_from"),
        active_until=kwargs.get("active_until"),
    )


# ------------------------------------ #
# String representation of a challenge #
# ------------------------------------ #


class ChallengeStrTests(TestCase):
    """
    Tests that check whether challenges have a proper
    string representation.
    """

    def test_str_returns_title(self):
        """
        Tests whether the string representation of a challenge is
        that challenge's title.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        self.assertEqual(str(TestFactoryUtils.make_challenge(name="Find the flag")), "Find the flag challenge")


# ------------------------------------ #
# Activity / Inactivity for challenges #
# ------------------------------------ #


class ChallengeIsActiveTests(TestCase):
    """
    Tests whether challenges become active / inactive
    according to a time window, and if this behavior is
    proper.
    """

    def test_is_active_no_time_window(self):
        """
        Enabled challenge with no time window should be active.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        self.assertTrue(TestFactoryUtils.make_challenge().is_active)

    def test_is_active_disabled(self):
        """
        Disabled challenge should not be active regardless of
        time window.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        self.assertFalse(TestFactoryUtils.make_challenge(enabled=False).is_active)

    def test_is_active_active_from_in_future(self):
        """
        Challenge whose ``active_from`` has not yet arrived should
        not be active.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_from=timezone.now() + timedelta(hours=1))

        self.assertFalse(challenge.is_active)

    def test_is_active_active_from_in_past(self):
        """
        Challenge whose ``active_from`` has passed should be active.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_from=timezone.now() - timedelta(hours=1))
        self.assertTrue(challenge.is_active)

    def test_is_active_active_until_in_future(self):
        """
        Challenge with ``active_until`` in the future and no
        start should be active.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_until=timezone.now() + timedelta(hours=1))

        self.assertTrue(challenge.is_active)

    def test_is_active_active_until_in_past(self):
        """
        Challenge whose ``active_until`` has passed should not
        be active.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_until=timezone.now() - timedelta(hours=1))

        self.assertFalse(challenge.is_active)

    def test_is_active_within_time_window(self):
        """
        Challenge within its ``active_from`` / ``active_until``
        window should be active.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(
            active_from=timezone.now() - timedelta(hours=1),
            active_until=timezone.now() + timedelta(hours=1),
        )

        self.assertTrue(challenge.is_active)

    def test_is_active_active_from_boundary(self):
        """
        A challenge starting just now should be active. So the
        method should be inclusive.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_from=timezone.now() - timedelta(seconds=1))

        self.assertTrue(challenge.is_active)

    def test_is_active_active_until_boundary(self):
        """
        A challenge ending just now should be active. So the method
        should be inclusive.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_until=timezone.now() + timedelta(seconds=1))
        self.assertTrue(challenge.is_active)


# -------------------- #
# Revealing challenges #
# -------------------- #


class ChallengeIsRevealedTests(TestCase):
    """
    Tests that check whether challenges get revealed in accordance
    with the time window for which they are specified.
    """

    def test_is_revealed_no_time_window(self):
        """
        Enabled challenge in a revealed tournament with
        no time window should be revealed.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        self.assertTrue(TestFactoryUtils.make_challenge().is_revealed)

    def test_is_revealed_disabled(self):
        """
        Disabled challenge should not be revealed.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        self.assertFalse(TestFactoryUtils.make_challenge(enabled=False).is_revealed)

    def test_is_revealed_tournament_not_revealed(self):
        """
        Challenge in an unrevealed tournament should not be revealed.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        unrevealed = TestFactoryUtils.make_tournament(active_from=timezone.now() + timedelta(hours=1))
        self.assertFalse(TestFactoryUtils.make_challenge(tournament=unrevealed).is_revealed)

    def test_is_revealed_active_from_in_future(self):
        """
        Challenge whose ``active_from`` has not yet arrived
        should not be revealed.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_from=timezone.now() + timedelta(hours=1))

        self.assertFalse(challenge.is_revealed)

    def test_is_revealed_active_from_in_past(self):
        """
        Challenge whose ``active_from`` has passed should be revealed.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_from=timezone.now() - timedelta(hours=1))

        self.assertTrue(challenge.is_revealed)

    def test_is_revealed_active_until_does_not_gate_reveal(self):
        """
        A passed challenge deadline should not affect reveal
        - only the challenge begin date gates it.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(active_until=timezone.now() - timedelta(hours=1))

        self.assertTrue(challenge.is_revealed)

    def test_is_revealed_disabled_overrides_revealed_tournament(self):
        """
        A disabled challenge in a revealed tournament should
        still not be revealed.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        challenge = TestFactoryUtils.make_challenge(enabled=False, revealed=True)

        self.assertFalse(challenge.is_revealed)


# ------------------------ #
# Challenge model + queryset #
# ------------------------ #


class ChallengeModelTests(TestCase):
    """Tests the Challenge representation and constraints with saved instances."""

    def test_string_representation(self):
        challenge = make_saved_challenge(name="Find the flag")
        self.assertEqual(str(challenge), "Find the flag challenge")

    def test_slug_is_unique(self):
        make_saved_challenge(slug="dup")
        with self.assertRaises(IntegrityError):
            make_saved_challenge(slug="dup", tournament=make_tournament())


class ChallengeQuerysetTests(TestCase):
    """Tests the active/revealed querysets on the Challenge manager."""

    def setUp(self):
        now = timezone.now()
        self.tournament = make_tournament()
        self.live = make_saved_challenge(
            tournament=self.tournament,
            slug="live",
            active_from=now - timedelta(hours=1),
            active_until=now + timedelta(hours=1),
        )
        self.disabled = make_saved_challenge(tournament=self.tournament, slug="disabled", enabled=False)

    def test_active_excludes_disabled(self):
        active = Challenge.objects.active()
        self.assertIn(self.live, active)
        self.assertNotIn(self.disabled, active)

    def test_revealed_excludes_disabled(self):
        revealed = Challenge.objects.revealed()
        self.assertIn(self.live, revealed)
        self.assertNotIn(self.disabled, revealed)
