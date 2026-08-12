from rest_framework import serializers

from stores.api.serializers.items import UsableItemRetrievalSerializer
from stores.models.inventories import Inventory

# -------------------- #
# Retrieval Serializer #
# -------------------- #


class RetrievalSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ["id", "items"]
        read_only_fields = fields

    def get_items(self, obj):
        items = obj.items.filter(item__store__tournament=obj.tournament)

        return UsableItemRetrievalSerializer(items, many=True).data
