from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from challenges import models
from files.api.serializers import RetrieveSerializer as FileRetrievalSerializer
from tournaments.api.serializers import RetrievalSerializer as TournamentSerializer

# -------------------- #
# Retrieval Serializer #
# -------------------- #


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes all possible challenge
    fields for proper single display.

    ----

    **Relies** on the fields:

    - ``tournament``: A tournament serializer
    - ``thumbnail``: A file serializer

    ----

    **Contains** the additional fields:

    - ``description``: The description that is visible only
      if the challenge is

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    tournament = TournamentSerializer()
    thumbnail = FileRetrievalSerializer()

    description = SerializerMethodField()

    # --------------- #
    # Base Meta class #
    # --------------- #

    class Meta:
        model = models.Challenge
        fields = [
            "id",
            "name",
            "slug",
            "enabled",
            "active_until",
            "description",
            "tournament",
            "points",
            "description",
            "thumbnail",
            "active_from",
            "submission_visibility",
        ]
        read_only_fields = fields

    # ----------------- #
    # Additional Fields #
    # ----------------- #

    @extend_schema_field(serializers.CharField)
    def get_description(self, instance):
        """
        Extends the serializer schema by making it possible to
        retrieve the description only if the challenge is revealed
        to the public.

        :param instance: Challenge
        :return: String
        """

        if instance.is_revealed:
            return instance.description
        return ""


# ---------------------------- #
# Preview Retrieval Serializer #
# ---------------------------- #


# The whole idea of having a preview
# serializer is to avoid pulling all challenge information
# if itself is not necessary.
#
# Essentially, anything that is needed for a list display
# can be put here, the other fields can be ignored.


class PreviewRetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that only includes data necessary for a
    challenge multi-preview display.

    ----

    **Relies** on:

    - ``tournament``: A tournament serializer

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    tournament = TournamentSerializer()

    class Meta:
        model = models.Challenge
        fields = [
            "name",
            "slug",
            "enabled",
            "active_until",
            "description",
            "tournament",
            "points",
        ]
        read_only_fields = fields
