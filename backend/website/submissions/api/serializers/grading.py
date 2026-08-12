from rest_framework import serializers

from submissions.models import Submission

# ----------------- #
# Update Serializer #
# ----------------- #


class UpdateSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    grading a given submission.

    ----

    **Contains** the additional fields:

    - ``submission_id``: The id of the submission to grade
    - ``points``: The number of points that is awarded to the submission

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    submission_id = serializers.IntegerField(read_only=False)
    points = serializers.IntegerField(read_only=False)

    class Meta:
        model = Submission
        fields = ["submission_id", "points"]
        read_only_fields = fields


# ----------------------- #
# Lock Handler Serializer #
# ----------------------- #


class LockSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    grading a given submission.

    ----

    **Contains** the additional fields:

    - ``submission_id``: The id of the submission to lock

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    submission_id = serializers.IntegerField(read_only=False)

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        model = Submission
        fields = ["submission_id"]
        read_only_fields = fields
