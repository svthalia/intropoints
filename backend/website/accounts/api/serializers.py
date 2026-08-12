from rest_framework import serializers

from accounts.models.accounts import TournamentAccount
from accounts.models.transactions import Transaction

# -------------------- #
# Retrieval Serializer #
# -------------------- #


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that contains all necessary data for
    accessing a Tournament Account.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    class Meta:
        model = TournamentAccount
        fields = ("tournament", "type", "balance")


class TransactionRetrievalSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ("id", "amount", "accepted", "requested_at", "description")
        read_only_fields = fields

    def get_description(self, obj):
        return str(obj)
