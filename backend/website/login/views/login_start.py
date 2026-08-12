from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView
from oauth2_provider.models import get_application_model

# ---------------------- #
# OAuth Client Utilities #
# ---------------------- #


class OAuthUtils:
    """
    Encapsulates basic OAuth authentication utilities.

    ----

    **Provies** the functionality:

    - ``get_client_id``: Retrieving a client's application id
    """

    @staticmethod
    def get_client_id(client_name):
        """
        Tries to retrieve a client application id by name.
        If it fails, then it returns an empty string.

        ----

        :param client_name: The name of the client application
        :type client_name: str

        :return: The id of the client application
        :rtype: int
        """

        try:
            app = get_application_model().objects.get(name=client_name)
            return app.client_id
        except get_application_model().DoesNotExist:
            return None


# ---------------------------- #
# URL Authentication Utilities #
# ---------------------------- #


class AuthUrlUtils:
    """
    Encapsulates URL utilities that are used for
    constructing urls during the main authentication
    process.

    ----

    **Provies** the functionality:

    - ``get_auth_endpoint_url``: Retrieving the authentication endpoint URL
    - ``get_auth_redirect_url``: Retrieving the authentication redirect URL
    """

    @staticmethod
    def get_auth_endpoint_url():
        """
        Constructs the OAuth authentication endpoint URL
        from the application's settings.

        ----

        :param: None

        :return: The fully constructed authentication endpoint URL
        :rtype: str
        """

        return f"/{settings.OAUTH_API_AUTHORIZATION_ENDPOINT}"

    @staticmethod
    def get_auth_redirect_url(oauth_client_name, state):
        """
        Retrieves the authentication URL that should be called
        after a successful login through the provider's end.

        ----

        :param oauth_client_name: The application's client name
        :type oauth_client_name: str

        :param state: The state of the start login request
        :type state: str

        :return: The complete OAuth redirect URL
        :rtype: str
        """

        # Retrieve all the necessary data for
        # URL construction
        auth_url = AuthUrlUtils.get_auth_endpoint_url()
        data = {
            "client_id": OAuthUtils.get_client_id(oauth_client_name),
            "redirect_uri": settings.HOST_BASE_URI + settings.OAUTH_API_REDIRECT_ENDPOINT,
            "response_type": "token",
            "state": state,
        }
        query_data = urlencode(data)

        return f"{auth_url}?{query_data}"


# --------------------- #
# Login Start Procedure #
# --------------------- #


class StartLoginView(TemplateView):
    """
    View that handles starting the login and authentication
    process. Generates the starting URL and keeps track of the
    login state within the session until the session has ended.
    """

    def get(self, request, **kwargs):
        """
        Starts the authentication process and stores the
        session authentication state;

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: Redirect to the base login endpoint
        :rtype: HttpResponse
        """

        # Retrieve the oauth app name
        # TODO! Make some checks here for invalid application names
        #       or non-existent IDs.
        oauth_client_name = request.GET.get("oauth_app")
        oauth_state = str(uuid4())

        url = AuthUrlUtils.get_auth_redirect_url(oauth_client_name, oauth_state)

        request.session["state"] = oauth_state

        return redirect(url)
