from rest_framework import serializers

from teams import models

# -------------------- #
# Retrieval Serializer #
# -------------------- #


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that prepares a team's display fields for
    object retrieval.

    ----

    **Contains** the additional fields:

    - ``members``: The string representation of members is the member username
    - ``total_points``: The total points that the team has earned

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    members = serializers.StringRelatedField(many=True)
    total_points = serializers.SerializerMethodField()

    class Meta:
        model = models.Team
        fields = ("id", "name", "members", "total_points")

    # --------------------- #
    # Additional Properties #
    # --------------------- #

    def get_total_points(self, obj):
        """
        Retrieves the total points that the team has
        earned until this point.

        ----

        :param obj: The team instance
        :type obj: Team

        :return: Total points that the team has earned
        :rtype: int
        """

        return obj.get_main_account().balance


# --------------------- #
# Scoreboard Serializer #
# --------------------- #-


class ScoreboardSerializer(serializers.ModelSerializer):
    """
    Serializer that prepares a team's scoreboard display
    fields

    ----

    **Contains** the additional fields:

    - ``members``: The string representation of members is the member username
    - ``points``: Dynamically retrieved points value

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    members = serializers.StringRelatedField(many=True)
    points = serializers.ReadOnlyField(default=0)

    class Meta:
        model = models.Team
        fields = ("name", "members", "points")
