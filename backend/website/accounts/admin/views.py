from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.models.transactions import Transaction

# ------------------------ #
# Reverse Transaction View #
# ------------------------ #


class ReverseTransactionView(TemplateView):
    """
    View that handles reverting a transaction by simply
    retrieving it and calling the corresponding method.
    """

    def get(self, request, **kwargs):
        """
        Retrieves the given transaction and
        calls ``reverse`` on it.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: A redirect to the initial caller
        :rtype: HttpResponseRedirect
        """

        # Retrieve the transaction and reverse it
        transaction = Transaction.objects.get(pk=kwargs.get("transaction_id"))
        transaction.reverse()

        # Redirect back to the change page
        return redirect(request.META.get("HTTP_REFERER"))
