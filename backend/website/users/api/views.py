from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from users.api.serializers import RetrievalSerializer as UserRetrievalSerializer

# ---------------------- #
# Current user retrieval #
# ---------------------- #


class CurrentUserAPIView(RetrieveAPIView):
    """
    View that handles retrieving the current user's
    information in a serialized format via the
    Rest Framework.
    """

    serializer_class = UserRetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieves the current user's account information.

        ----

        :return: Returns the current user's account information
        :rtype: User
        """

        return get_user_model().objects.get(pk=self.request.user.id)
