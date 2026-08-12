import secrets
import uuid

from django.conf import settings
from django.db import models

# ---------------- #
# Login User Model #
# ---------------- #


# Wrapper around the base user model that represents itself
# in an authentication context
class OAuthUser(models.Model):
    """
    Class that represents a user of the system.
    This is a wrapper around the base user for any
    OAuth authentication request.

    Makes it significantly easier to retrieve
    users from different platforms.

    ----

    **Contains** the fields:

    - ``model``: The user database model
    - ``uid``: The imported user's id
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, help_text="The user database model", on_delete=models.CASCADE, related_name="user"
    )
    """ The user that is being wrapped by this class """

    uid = models.BigIntegerField()
    """ The imported user's uid """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    # --------------- #
    # Base meta class #
    # --------------- #

    class Meta:
        verbose_name = "OAuth User"

    # ------------ #
    # Base methods #
    # ------------ #

    def __str__(self):
        """
        Converts the user to a string object.
        Simply prints the user's ID.

        ----

        :param: None

        :return: The string representation of the user
        :rtype: str
        """

        return f"User with id {self.uid}"


# --------------------- #
# Authentication Models #
# --------------------- #


class AuthenticationRequest(models.Model):
    """
    Class that models a basic authentication request, can
    be extended to resolve more complex authentication requests.

    ----

    Contains:

    - ``state``: The authentication state as an uuid
    - ``requested_at``: The date when the request was made
    - ``challenge``: The challenge of the request
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    state = models.UUIDField(
        help_text="The request number / state", primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    """ The store OAuth authentication state against CSRF """

    requested_at = models.DateTimeField(help_text="The date and time the request was made", auto_now_add=True)
    """ The date the request was made at """

    challenge = models.CharField(
        help_text="The challenge of the made request", max_length=80, default=secrets.token_urlsafe(48)
    )
    """ The authentication challenge """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the request to a string object.
        This is based on the request's id and
        requested date.

        ----

        :param: None

        :return: The string representation of the request
        :rtype: str
        """

        return f"Request with id {self.id} created on {self.requested_at}"
