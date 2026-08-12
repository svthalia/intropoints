from rest_framework import serializers

from submissions.models import Submission

# ------------------- #
# Creation Serializer #
# ------------------- #


class CreationSerializer(serializers.ModelSerializer):
    """
    Serializer that includes all the fields for a
    submission, in order to create one from an
    upload request.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

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
            "file",
        ]
        read_only_fields = []
