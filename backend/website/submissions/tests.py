from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from challenges.models import Challenge
from submissions.models import Submission
from teams.models import Team
from tournaments.models import Tournament


def make_challenge(slug="test-challenge"):
    now = timezone.now()
    tournament = Tournament.objects.create(
        name="t", slug="t", active_from=now - timedelta(hours=1), active_until=now + timedelta(hours=1)
    )
    return Challenge.objects.create(name="Test Challenge", slug=slug, description="d", tournament=tournament, points=10)


class SubmissionModelTests(TestCase):
    """Tests the Submission model representation and fields."""

    def test_string_representation(self):
        team = Team.objects.create(name="Thalia")
        challenge = make_challenge()
        submission = Submission.objects.create(team=team, challenge=challenge)

        self.assertEqual(str(submission), "Submission by Thalia for the challenge: Test Challenge")

    def test_accepted_defaults_to_none(self):
        submission = Submission.objects.create(team=Team.objects.create(name="T"), challenge=make_challenge())
        self.assertIsNone(submission.accepted)

    def test_received_points_defaults_to_zero(self):
        submission = Submission.objects.create(team=Team.objects.create(name="T"), challenge=make_challenge())
        self.assertEqual(submission.received_points, 0)

    def test_is_viewed_defaults_to_false(self):
        submission = Submission.objects.create(team=Team.objects.create(name="T"), challenge=make_challenge())
        self.assertFalse(submission.is_viewed)

    def test_links_team_and_challenge(self):
        team = Team.objects.create(name="Linkers")
        challenge = make_challenge()
        submission = Submission.objects.create(team=team, challenge=challenge)

        self.assertEqual(submission.team, team)
        self.assertEqual(submission.challenge, challenge)
        self.assertIn(submission, team.submission.all())
