from rest_framework import serializers

from files.api.serializers import RetrieveSerializer as FileRetrievalSerializer
from submissions.models import Submission

# -------------------- #
# Retrieval Serializer #
# -------------------- #


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    grading a given submission.

    ----

    **Contains** the additional fields:

    - ``file_source``: The source of the file to be uploaded

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    file_source = serializers.FileField(write_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "challenge",
            "tournament",
            "accepted",
            "created_by",
            "updated_by",
            "created_time",
            "team",
            "file_source",
        ]
        read_only_fields = fields


# ---------------------------- #
# Preview Retrieval Serializer #
# ---------------------------- #


class PreviewRetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    grading a given submission.

    ----

    **Relies** on the fields:

    - ``file``: The file that is included in the submission

    **Contains** the additional fields:

    - ``challenge_name``: The name of the challenge that the submission
    - ``team_name``: The name of the team that the submission
    - ``created_by``: The name of the user who submitted the

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    file = FileRetrievalSerializer()

    challenge_name = serializers.SerializerMethodField()
    challenge_slug = serializers.SerializerMethodField()
    challenge_submission_visibility = serializers.SerializerMethodField()
    tournament_name = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        model = Submission
        fields = [
            "id",
            "challenge_name",
            "challenge_slug",
            "challenge_submission_visibility",
            "tournament_name",
            "team_name",
            "created_by",
            "created_time",
            "file",
            "accepted",
            "received_points",
        ]
        read_only_fields = fields

    # ------------------#
    # Additional Fields #
    # ------------------#

    def get_challenge_name(self, obj):
        """
        Retrieves the name of the challenge that the
        submission belongs to.

        ----

        :param obj: The submission instance
        :type obj: Submission

        :return: The name of the challenge
        :rtype: str
        """

        return obj.challenge.name

    def get_challenge_slug(self, obj):
        """
        Retrieves the slug of the challenge that the submission
        belongs to.

        @param obj -> the submission instance;
        @return    -> aforementioned slug;
        """

        return obj.challenge.slug

    def get_challenge_submission_visibility(self, obj):
        """
        Retrieves the submission visibility of the challenge
        that the submission belongs to.

        @param obj -> the submission instance;
        @return    -> a number which corresponds to the visibility option
        """

        return obj.challenge.submission_visibility

    def get_tournament_name(self, obj):
        """
        Retrieves the name of the tournament that the submission
        belongs to.

         ----

        :param obj: The submission instance
        :type obj: Submission

        :return: The name of the tournament
        :rtype: str
        """

        return obj.tournament.slug

    def get_team_name(self, obj):
        """
        Retrieves the name of the team that the submission
        belongs to.

        ----

        :param obj: The submission instance
        :type obj: Submission

        :return: The name of the team
        :rtype: str
        """

        return obj.team.name

    def get_created_by(self, obj):
        """
        Retrieves the name of the user who submitted the
        current submission.

        ----

        **Overrides** the initial ``created_by`` field in favor
         a more easily displayable one.

        ----

        :param obj: The submission instance
        :type obj: Submission

        :return: The name of the user
        :rtype: str
        """

        return obj.created_by.display_name
