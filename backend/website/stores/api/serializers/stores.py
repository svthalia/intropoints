from rest_framework import serializers

from stores.models.stores import Store

# -------------------- #
# Retrieval Serializer #
# -------------------- #


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    displaying a given store.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    tournament = serializers.ReadOnlyField(source="tournament.id")
    tournament_slug = serializers.ReadOnlyField(source="tournament.slug")

    class Meta:
        model = Store
        fields = ("id", "name", "description", "tournament", "tournament_slug")
        read_only_fields = fields
