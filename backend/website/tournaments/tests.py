from datetime import timedelta

from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from core.tests.utils import TestFactoryUtils
from tournaments.models import Tournament

# --------------------------- #
# Tournament Properties Tests #
# --------------------------- #


class TournamentPropertyTests(TestCase):
    """
    Tests that cover the tournament properties and their
    interaction within the application
    """

    # ----------- #
    # Test set up #
    # ----------- #

    def setUp(self):
        """
        Method that runs before each test function in order
        to set up base tournament instances.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        now = timezone.now()

        self.active1 = TestFactoryUtils.make_tournament(slug="1", active_from=now, active_until=now + timedelta(1))
        self.active1.save()

        self.active2 = TestFactoryUtils.make_tournament(
            slug="2", active_from=now - timedelta(1, 1, 1), active_until=now + timedelta(1, 1, 1)
        )
        self.active2.save()

        self.expired1 = TestFactoryUtils.make_tournament(
            slug="3", active_from=now - timedelta(2, 2, 2), active_until=now - timedelta(1, 1, 1)
        )
        self.expired1.save()

        self.expired2 = TestFactoryUtils.make_tournament(
            slug="4", active_from=now - timedelta(40), active_until=now - timedelta(20)
        )
        self.expired2.save()
        self.future1 = TestFactoryUtils.make_tournament(
            slug="5", active_from=now + timedelta(3, 3, 2), active_until=now + timedelta(3, 3, 6)
        )

        self.future1.save()
        self.future2 = TestFactoryUtils.make_tournament(
            slug="6", active_from=now + timedelta(40), active_until=now + timedelta(88)
        )
        self.future2.save()

        self.always = TestFactoryUtils.make_tournament(slug="7")
        self.always.save()

    # --------------- #
    # Integrity tests #
    # --------------- #

    def test_all(self):
        """
        Tests that all created instances fall under
        the tournament query set.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        all_tournaments = Tournament.objects.all()

        self.assertIn(self.active1, all_tournaments)
        self.assertIn(self.active2, all_tournaments)
        self.assertIn(self.expired1, all_tournaments)
        self.assertIn(self.expired2, all_tournaments)
        self.assertIn(self.future1, all_tournaments)
        self.assertIn(self.future2, all_tournaments)
        self.assertIn(self.always, all_tournaments)

    def test_active(self):
        """
        Tests that only currently active challenges
        are returned when querying the manager for
        active tournaments.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        active_tournaments = Tournament.objects.active()

        self.assertIn(self.active1, active_tournaments)
        self.assertIn(self.active2, active_tournaments)
        self.assertNotIn(self.expired1, active_tournaments)
        self.assertNotIn(self.expired2, active_tournaments)
        self.assertNotIn(self.future1, active_tournaments)
        self.assertNotIn(self.future2, active_tournaments)
        self.assertIn(self.always, active_tournaments)

        self.assertTrue(self.active2.active)

    def test_revealed(self):
        """
        Tests that only currently revealed challenges
        are returned when querying the manager for
        revealed tournaments.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        revealed_tournaments = Tournament.objects.revealed()

        self.assertIn(self.active1, revealed_tournaments)
        self.assertIn(self.active2, revealed_tournaments)
        self.assertIn(self.expired1, revealed_tournaments)
        self.assertIn(self.expired2, revealed_tournaments)
        self.assertNotIn(self.future1, revealed_tournaments)
        self.assertNotIn(self.future2, revealed_tournaments)
        self.assertIn(self.always, revealed_tournaments)

        self.assertTrue(self.expired1.revealed)

    def test_slug(self):
        """
        Tests whether no two tournaments with the same slug
        can exist within the database.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        with self.assertRaises(IntegrityError):
            self.original = TestFactoryUtils.make_tournament(slug="8")
            self.original.save()
            self.duplicate = TestFactoryUtils.make_tournament(slug="8")
            self.duplicate.save()

    def test_range(self):
        """
        Tests whether tournaments that do not have a
        valid active period can exist.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        with self.assertRaises(IntegrityError):
            self.invert_rage = TestFactoryUtils.make_tournament(
                slug="9", active_from=timezone.now(), active_until=timezone.now() - timedelta(30)
            )

            self.invert_rage.save()


# ------------------------ #
# Tournament model basics  #
# ------------------------ #


class TournamentModelTests(TestCase):
    """Tests the Tournament model representation and constraints."""

    def test_string_representation(self):
        tournament = Tournament.objects.create(name="Spring Cup", slug="spring-cup")
        self.assertEqual(str(tournament), "Tournament Spring Cup")

    def test_slug_is_unique(self):
        Tournament.objects.create(name="A", slug="dup")
        with self.assertRaises(IntegrityError):
            Tournament.objects.create(name="B", slug="dup")

    def test_start_after_end_is_rejected(self):
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            Tournament.objects.create(name="Bad", slug="bad", active_from=now, active_until=now - timedelta(hours=1))


class TournamentStatusTests(TestCase):
    """Tests the revealed/active properties and matching querysets."""

    def setUp(self):
        now = timezone.now()
        self.upcoming = Tournament.objects.create(
            name="Upcoming",
            slug="upcoming",
            active_from=now + timedelta(hours=1),
            active_until=now + timedelta(hours=2),
        )
        self.live = Tournament.objects.create(
            name="Live", slug="live", active_from=now - timedelta(hours=1), active_until=now + timedelta(hours=1)
        )
        self.finished = Tournament.objects.create(
            name="Finished",
            slug="finished",
            active_from=now - timedelta(hours=2),
            active_until=now - timedelta(hours=1),
        )

    def test_revealed_property(self):
        self.assertTrue(self.live.revealed)
        self.assertFalse(self.upcoming.revealed)

    def test_active_property(self):
        self.assertTrue(self.live.active)
        self.assertFalse(self.finished.active)

    def test_revealed_queryset(self):
        revealed = Tournament.objects.revealed()
        self.assertIn(self.live, revealed)
        self.assertIn(self.finished, revealed)
        self.assertNotIn(self.upcoming, revealed)

    def test_active_queryset(self):
        active = Tournament.objects.active()
        self.assertIn(self.live, active)
        self.assertNotIn(self.finished, active)
        self.assertNotIn(self.upcoming, active)
