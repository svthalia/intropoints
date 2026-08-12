from rest_framework.generics import ListAPIView

from accounts.api.serializers import RetrievalSerializer, TransactionRetrievalSerializer
from accounts.models.accounts import TournamentAccount
from accounts.models.transactions import Transaction


class ForTeamTournamentAPIView(ListAPIView):
    serializer_class = RetrievalSerializer

    def get_queryset(self):
        return TournamentAccount.objects.filter(
            team_id=self.kwargs["team_id"],
            tournament__slug=self.kwargs["tournament_slug"],
        )


class TransactionsForTeamTournamentAPIView(ListAPIView):
    serializer_class = TransactionRetrievalSerializer

    def get_queryset(self):
        account_ids = TournamentAccount.objects.filter(
            team_id=self.kwargs["team_id"],
            tournament__slug=self.kwargs["tournament_slug"],
        ).values_list("id", flat=True)

        return Transaction.objects.filter(
            account_id__in=account_ids,
        ).order_by("-requested_at")
