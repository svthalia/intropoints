from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from stores.api.serializers.inventories import RetrievalSerializer as InventoryRetrievalSerializer
from stores.api.serializers.items import UsableItemConsumerSerializer
from stores.models.inventories import Inventory
from stores.models.items import UsableItem
from teams.api.utils import TeamAPIUtilities
from teams.models import Team
from tournaments.models import Tournament

# -------------------------------- #
# Current Team Inventory Retrieval #
# -------------------------------- #


class CurrentTeamInventoryForTournamentAPIView(RetrieveAPIView):
    """
    Retrieves the team of the user that has made
    the api request.
    """

    queryset = Team.objects.all()

    serializer_class = InventoryRetrievalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    def get_object(self):
        """
        Retrieves the inventory for the current team
        of the user, given the tournament selected in
        the request URL.
        """

        # Try to retrieve the tournament
        tournament_slug = self.kwargs.get("slug")
        tournament = get_object_or_404(Tournament, slug=tournament_slug)

        # Try to retrieve the team
        team = TeamAPIUtilities.get_team_from_request(self.request)

        return Inventory.objects.get(tournament=tournament, team=team)


# --------------------- #
# Current Team Item Use #
# --------------------- #


class CurrentTeamUseItemForAPIView(UpdateAPIView):
    """
    On access, uses the item from a tournament's
    team inventory.
    """

    queryset = UsableItem.objects.all()
    lookup_field = "id"

    serializer_class = UsableItemConsumerSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    def put(self, request, *args, **kwargs):
        """
        When called, uses the given item, and creates a receipt
        for it that can be later reviewed.
        """

        usable_item = self.get_object()
        usable_item_id = usable_item.id
        usable_item.use()

        # Check if the item is still present
        try:
            UsableItem.objects.get(id=usable_item_id)
        except UsableItem.DoesNotExist:
            return Response(
                {
                    "detail": "Item successfully used",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Item failed to be used",
            },
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
