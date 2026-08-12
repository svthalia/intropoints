from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from challenges.models import Challenge
from files.models.base import File
from submissions.api.serializers.retrieval import PreviewRetrievalSerializer as SubmissionRetrievalPreviewSerializer
from submissions.api.serializers.upload import CreationSerializer as SubmissionCreationSerializer
from submissions.models import Submission
from teams.models import Team

# -------------------- #
# Upload API Endpoints #
# -------------------- #


class UploadAPIView(CreateAPIView):
    """
    API endpoint that allows submissions to be uploaded.
    Handles user files submission and tracking.
    """

    serializer_class = SubmissionCreationSerializer
    queryset = Submission.objects.all()

    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def post(self, request, *args, **kwargs):
        """
        Creates a serialized submission object based on the
        POST data to the API endpoint.
        """

        # Request the team and challenge IDs for the form
        team_id = request.data.get("team", None)
        challenge_id = request.data.get("challenge", None)
        file_id = request.data.get("file", None)

        # Try to retrieve both the team and challenge
        team = get_object_or_404(Team, id=team_id)
        challenge = get_object_or_404(Challenge, id=challenge_id)
        file = get_object_or_404(File, id=file_id)

        # Remove any previously existing submission
        # in order to overwrite it
        Submission.objects.filter(tournament=challenge.tournament, team=team, challenge=challenge).delete()

        # Serialize the inputted object
        serializer = self.get_serializer(
            data={
                "accepted": None,
                "team": team.id,
                "challenge": challenge.id,
                "tournament": challenge.tournament.id,
                "updated_by": self.request.user.id,
                "created_by": self.request.user.id,
                "file": file.id,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Get the result of saving the serializer
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# ----------------------- #
# Retrieval API Endpoints #
# ----------------------- #


# Handles general submissions for
# the submission feed page
class AllAPIView(ListAPIView):
    """
    API endpoint that allows for all accepted submissions
    to be retrieved in the order that they created in.
    """

    serializer_class = SubmissionRetrievalPreviewSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    # -------------------- #
    # API Object Retrieval #
    # -------------------- #

    def get_queryset(self):
        """
        Pulls all submissions, accepted submissions sorted
        in the most recent order.
        """

        return Submission.objects.order_by("created_time")


# Handle submissions when searching
# for the ones for your own team
class ForTeamAPIView(ListAPIView):
    """
    API endpoint that allows submissions for the same team to
    be retrieved. Handles filtering and retrieving a list of all
    relevant submissions.
    """

    serializer_class = SubmissionRetrievalPreviewSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def get_queryset(self):
        """
        Pulls the submissions matching the given team query,
        with the most recent ones being display first.
        """

        return Submission.objects.filter(team__name=self.kwargs.get("team_name")).order_by("created_time")


# ---------------------------------- #
# Submission retrieval per challenge #
# ---------------------------------- #


# Handle submissions when searching
# for the ones for your own team
class ForChallengeAPIView(ListAPIView):
    """
    API endpoint that allows submissions for the same challenge to
    be retrieved. Handles filtering and retrieving a list of all
    relevant submissions.

    ----

    Adheres to the challenge's visibility choices, only
    allowing submissions to be visible based on circumstances.
    """

    serializer_class = SubmissionRetrievalPreviewSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    # -------------------- #
    # API Object Retrieval #
    # -------------------- #

    def get_queryset(self):
        """
        Pulls the submissions matching the given challenge query,
        with the most recent ones being display first.
        """

        return Submission.objects.filter(challenge__slug=self.kwargs.get("slug")).order_by("created_time")
