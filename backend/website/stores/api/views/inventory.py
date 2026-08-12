from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from stores.api.serializers.inventories import RetrievalSerializer
from stores.models.inventories import Inventory


class ForTeamTournamentAPIView(RetrieveAPIView):
    """
    Retrieve the inventory for a team in a specific tournament.
    """

    serializer_class = RetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        inventory, _ = Inventory.objects.get_or_create(
            team_id=self.kwargs["team_id"],
            tournament__slug=self.kwargs["tournament_slug"],
        )

        return inventory
