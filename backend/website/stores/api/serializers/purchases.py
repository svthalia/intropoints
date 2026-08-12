from rest_framework import serializers

from stores.models.purchases import Purchase

# ------------------- #
# Creation Serializer #
# ------------------- #


class CreationSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    creating a purchase.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    class Meta:
        model = Purchase
        fields = ("team", "item")
        read_only_fields = ()
