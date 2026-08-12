from rest_framework import serializers

from tournaments import models


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes all possible tournament
    fields for proper single and multi- display.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    # --------------- #
    # Base Meta class #
    # --------------- #

    class Meta:
        model = models.Tournament
        fields = [
            "id",
            "name",
            "slug",
            "active_from",
            "active_until",
        ]
        read_only_fields = fields
