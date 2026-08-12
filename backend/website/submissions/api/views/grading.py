from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from submissions.api.serializers.grading import LockSerializer as SubmissionGradingLockSerializer
from submissions.api.serializers.grading import UpdateSerializer as SubmissionGradingUpdateSerializer
from submissions.api.serializers.retrieval import PreviewRetrievalSerializer as SubmissionPreviewRetrievalSerializer
from submissions.models import Submission
from users.api.permissions import IsICMember

# -------------- #
# Lock handling  #
# -------------- #


# Release the submission Lock.
# Also gets released automatically on, submission
# update or if the time expires.
class ReleaseAPIView(APIView):
    """
    API endpoint that releases the lock on a given submission.
    Mainly used to handle improper submission lock holds.
    """

    serializer_class = SubmissionGradingLockSerializer
    permission_classes = [IsAuthenticated, IsICMember]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def post(self, request, submission_id, *args, **kwargs):
        """
        Unlocks the selected submission from the database.
        """

        submission = get_object_or_404(Submission, id=submission_id)

        # Release submission only if needed
        if submission.is_viewed:
            submission.is_viewed = False
            submission.viewed_at = None
            submission.save()

            return Response({"status": "Unlocked!"}, status=status.HTTP_200_OK)
        return Response({"status": "Submission already Unlocked!"}, status=status.HTTP_200_OK)


# --------------------------------- #
# Retrieve all eligible submissions #
# --------------------------------- #


class AllAPIView(ListAPIView):
    """
    API endpoint that retrieves all submissions that
    are eligible for grading.
    """

    serializer_class = SubmissionPreviewRetrievalSerializer
    permission_classes = [IsAuthenticated, IsICMember]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_queryset(self):
        """
        Retrieves all submissions that are eligible for grading
        from the database. This includes the ones that have their lock
        expired.
        """

        lock_timeout = timezone.now() - timedelta(minutes=settings.SUBMISSION_LOCK_TIMEOUT)

        # Retrieving only submissions that are either released,
        # or on which the lock expired
        submission = Submission.objects.filter((Q(is_viewed=False) | Q(viewed_at__lt=lock_timeout)) & Q(accepted=None))

        return submission


# ------------- #
# Single Select #
# ------------- #


# Retrieves a random submission for grading, then locks
# the submission, such that it cannot be accessed by another client.
class SelectAPIView(RetrieveAPIView):
    """
    API endpoint that allows for random submission retrieval.
    Retrieval is allowed once per user, locking the submission
    while it is being viewed to avoid multiple grading.
    """

    serializer_class = SubmissionPreviewRetrievalSerializer
    permission_classes = [IsAuthenticated, IsICMember]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get(self, request, *args, **kwargs):
        """
        Retrieves the selected submission for grading
        from the database. Locks it in the process
        """

        # Only consider non-viewed submissions atomically.
        # Retrieve one of the available ones
        with transaction.atomic():
            lock_timeout = timezone.now() - timedelta(minutes=settings.SUBMISSION_LOCK_TIMEOUT)

            submission_id = kwargs.pop("id", None)
            submission = Submission.objects.select_for_update().get(
                (Q(id=submission_id) & Q(accepted=None)) & (Q(is_viewed=False) | Q(viewed_at__lt=lock_timeout))
            )
            if not submission:
                return Response({"status": "Submission locked!"}, status=status.HTTP_226_IM_USED)

            # Lock the submission
            submission.is_viewed = True
            submission.viewed_at = timezone.now()
            submission.save()

        # Serialize the submission and include it in the response
        serializer = self.get_serializer(submission)
        return Response(serializer.data)


# -------------------------- #
# Grade Update API Endpoints #
# -------------------------- #


# Creates a point transaction with the points awarded after grading.
# Unlocks the submission if locked
class GradeAPIView(UpdateAPIView):
    """
    API endpoint that handles adding or subtracting points from a
    team after the submission is graded.
    """

    serializer_class = SubmissionGradingUpdateSerializer
    permission_classes = [IsAuthenticated, IsICMember]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def put(self, request, *args, **kwargs):
        """
        Retrieves the submission id and point transaction in a
        POST request, and updates the points in the database.
        """

        with transaction.atomic():
            # Retrieve necessary team metadata
            submission_id = request.data.get("submission_id", None)
            submission = get_object_or_404(Submission, id=submission_id, accepted=None)
            accepted = request.data.get("accepted")
            tournament = submission.tournament
            team = submission.team

            # Retrieve the points
            points = int(request.data.get("points", 0))

            team.grade(tournament, points)

            submission.received_points = points
            submission.is_viewed = False
            submission.accepted = accepted
            submission.save()

        return Response({"status": "Points added!"}, status=status.HTTP_200_OK)
