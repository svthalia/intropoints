from rest_framework import serializers

from stores.models.items import Item, UsableItem

# ------------------------- #
# Item Retrieval Serializer #
# ------------------------ #


class ItemRetrievalSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ("id", "name", "description", "price", "thumbnail")
        read_only_fields = fields

    def get_thumbnail(self, obj):
        if not obj.thumbnail or not obj.thumbnail.source:
            return None

        return obj.thumbnail.source.url


# --------------------- #
# Usable Item Retrieval #
# --------------------- #


class UsableItemRetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes only relevant fields for
    displaying a given usable item.

    ----

    **Relies** on the fields:

    - ``item``: The serialized foreign item

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    item = ItemRetrievalSerializer(read_only=True)

    class Meta:
        model = UsableItem
        fields = ("id", "item")
        read_only_fields = fields


# -------------------- #
# Usable Item Consumer #
# -------------------- #


class UsableItemConsumerSerializer(serializers.ModelSerializer):
    """
    Serializer that is mean to simply allow for an
    item to be consumed.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.

    """

    class Meta:
        model = UsableItem
        fields = ()
        read_only_fields = fields
