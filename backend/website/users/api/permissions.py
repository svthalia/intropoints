from rest_framework.permissions import BasePermission
from rest_framework.request import Request  # noqa: F401
from rest_framework.viewsets import ReadOnlyModelViewSet  # noqa: F401

# --------------------------- #
# Custom API User permissions #
# --------------------------- #


# Custom permissions for the application
# User class should be implemented here.


class IsICMember(BasePermission):
    """
    API wrapper for the rest framework to distinguish
    IC members from other users.
    """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def has_permission(self, request, view):
        """
        Returns true if the user in the request is
        an IC member.

        :param request: The HTTP request that was made
        :type request: Request

        :param view: The API view accessing the permission
        :type view: ReadOnlyModelViewSet

        :return: Whether the user is an IC member or not
        :rtype: bool
        """

        return request.user.is_ic_member()
