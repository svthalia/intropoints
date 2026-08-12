from django.urls import path

from stores.api.views.inventory import ForTeamTournamentAPIView
from stores.api.views.items import AllAPIView as ItemsAllAPIView
from stores.api.views.items import CreatePurchaseAPIView as ItemsCreatePurchaseAPIView
from stores.api.views.items import ForStoreAPIView as ItemsForStoreAPIView
from stores.api.views.items import UseItemAPIView
from stores.api.views.stores import AllAPIView as StoresAllAPIView
from stores.api.views.stores import ForTournamentAPIView as StoresForTournamentAPIView

app_name = "stores"

# Store api endpoints for retrieving and
# using items
#
#
# ``/api/stores/all/
#   -> Get all available stores
#
# ``/api/stores/for-tournament/<slug:tournamnet_slug>/
#   -> Get all available stores for a given tournament
#
#
# ``/api/stores/items/all/
#   -> Get all available items
#
# ``/api/stores/items/for-store/<int:id>/
#   -> Get all available items for a given store
#
# ``/api/stores/items/purchase/
#   -> Make an item purchase

urlpatterns = [
    path("all/", StoresAllAPIView.as_view(), name="stores_all"),
    path("for-tournament/<slug:tournament__slug>/", StoresForTournamentAPIView.as_view(), name="stores_for_tournament"),
    path("items/all/", ItemsAllAPIView.as_view(), name="items_all"),
    path("items/for-store/<int:store__id>/", ItemsForStoreAPIView.as_view(), name="items_for_store"),
    path("items/purchase/", ItemsCreatePurchaseAPIView.as_view(), name="items_purchase"),
    path(
        "inventory/for-team-and-tournament/<int:team_id>/<slug:tournament_slug>/",
        ForTeamTournamentAPIView.as_view(),
        name="inventory_for_team_tournament",
    ),
    path("items/use/<int:usable_item_id>/", UseItemAPIView.as_view(), name="usable_item_use"),
]
