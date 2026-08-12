from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views.generic import TemplateView
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session

from login.models import AuthenticationRequest, OAuthUser

# This is where you call back classes for 3rd
# party login should be situated, they should include the proper
# user creation and login response to the 3rd party response.
#
# If no callback is needed, handle everything in `login_request.py`

# ------------------------- #
# Abstract Callback Classes #
# ------------------------- #


class CallbackView(TemplateView):
    """
    View that is accessed when the authorization is a 3rd party
    process and succeeds within the previous step.

    After a successful token exchange, it loads up
    the user information and saves it for later use.

    ----

    **Abstract** methods:

    - ``_exchange_token_(...)``: Exchanges the token with the third-party involved
    - ``_setup_user_(...)``: Sets up the user based on the available information
    """

    def get(self, request, **kwargs):
        """
        Accesses the Callback view if needed.
        Automatically retrieves the code, and authentication state
        and passes them to the '_exchange_token_()' method.

        On successful exchange, sets up the user according to the
        concrete implementation.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: Redirects to home or to completing the authentication process
        :rtype: HttpResponse
        """

        # Retrieve the authentication request state and compare
        # with the previously stored one in the client.
        code = request.GET.get("code", None)
        state_in_request = request.GET.get("state", None)
        state_in_cookie = request.COOKIES.get("state")

        # On fault, abort.
        if state_in_request != state_in_cookie:
            return HttpResponse(status=400)

        # Try to exchange authentication token,
        # and set up the user
        oauth_client = self._exchange_token_(request, code, state_in_request)
        if self._setup_user_(request, oauth_client):
            next_query = request.GET.get("next", None)
            if next_query is not None:
                return redirect(next_query)
            return redirect("/navigation")

        # Catch failures
        return HttpResponse("Could not complete authentication!", status=401)

    def _exchange_token_(self, request, code, state):
        """
        **!! Virtual method, implement it in subclass !!**

        ----

        Exchanges the token with the third-party involved.
        Such as Thalia, Google ...

        This should retrieve the third party client
        endpoint that can accesses user information.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param code: The received authentication token
        :type code: str

        :param state: The received authentication state
        :type state: str

        :return: A reference OAuth client with 3rd party access
        :rtype: OAuthClient
        """

    def _setup_user_(self, request, oauth_client):
        """
        **!! Virtual method, implement it in subclass !!**

        ----

        Sets up the user based on the available information
        from the 2nd party.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param oauth_client: An OAuth client with 3rd party API access
        :rtype: OAuthClient

        :return: True only if the whole process is successful, False otherwise
        :rtype: bool
        """


# ------------------------- #
# Concrete Callback Classes #
# ------------------------- #


class ThaliaCallbackView(CallbackView):
    """
    Callback view that completes the 3rd-party authorization
    with the Thalia API.

    Handles retrieving user information from the Thalia API.
    """

    # ------------------------ #
    # Overridden Functionality #
    # ------------------------ #

    def _exchange_token_(self, request, code, state):
        """
        Exchanges the authentication token from the Thalia API,
        within a OAuth session to retrieve the full login.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param code: The received authentication token
        :type code: str

        :param state: The received authentication state
        :type state: str

        :return: A reference OAuth client with Thalia API access
        :rtype: OAuthClient
        """

        # Try to retrieve previous authentication request if it's
        # still alive - otherwise abort.
        # If the authentication got back in the same state,
        # the request is no longer needed, so it can be deleted.
        try:
            authentication_request = AuthenticationRequest.objects.get(state=state)
            authentication_request.delete()
        except AuthenticationRequest.DoesNotExist:
            return HttpResponse(status=404)

        # Start a client session within OAuth in order to
        # exchange the authorization token, and be able to
        # fetch information
        client = WebApplicationClient(client_id=settings.THALIA_API_OAUTH_CLIENT_ID)
        oauth_client = OAuth2Session(
            # The web app client
            client=client,
            # The uri towards which to redirect during the session
            redirect_uri=settings.THALIA_API_OAUTH_REDIRECT_URI + "?" + urlencode({"next": request.GET.get("next")}),
            # The access given within the oauth session
            scope=["profile:read"],
        )

        # Retrieve the authorization token
        oauth_client.fetch_token(
            # The uri from which to retrieve the token
            token_url=f"{settings.THALIA_API_BASE_URI}{settings.THALIA_API_ACCESS_TOKEN_ENDPOINT}",
            # The authorization token code
            code=code,
            # The thalia oauth client from which to get the token from
            client_id=settings.THALIA_API_OAUTH_CLIENT_ID,
            # The thalia client secret for access
            client_secret=settings.THALIA_API_OAUTH_CLIENT_SECRET,
            # The challenge to verify
            code_verifier=authentication_request.challenge,
        )

        return oauth_client

    def _setup_user_(self, request, oauth_client):
        """
        Retrieves all the necessary information from the
        Thalia API. Sets up the user's credentials, and
        registers it in a wrapper.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param oauth_client: An OAuth client with 3rd party access
        :rtype: OAuthClient

        :return: True if the Thalia user was registered, False otherwise
        :rtype: bool
        """

        # Retrieve the user member info in order to validate
        # the session. If it fails, abort.
        response = oauth_client.get(f"{settings.THALIA_API_BASE_URI}{settings.THALIA_API_MEMBERS_URL}")
        if response.status_code != 200:
            return False

        # Extract member data into individual fields
        member_data = response.json()
        thalia_identifier = member_data["pk"]
        thalia_display_name = member_data["profile"]["display_name"]
        thalia_short_display_name = member_data["profile"]["short_display_name"]
        thalia_initials = member_data["profile"]["initials"]
        photo = (
            member_data["profile"]["photo"]["medium"]
            if "photo" in member_data["profile"] and "medium" in member_data["profile"]["photo"]
            else None
        )

        # If the user does exist, retrieve said user for display.
        # Otherwise, create and add it to the database for future
        # sessions.
        try:
            thalia_user = OAuthUser.objects.get(uid=thalia_identifier)
        except OAuthUser.DoesNotExist:
            # Create the base user object and
            # initialize its parts
            user = get_user_model().objects.create_user(
                username=f"{thalia_short_display_name}_{str(thalia_identifier)}",
                display_name=thalia_display_name,
                initials=thalia_initials,
            )
            user.save()

            # Register it through the user wrapper
            thalia_user = OAuthUser.objects.create(
                uid=thalia_identifier,
                user=user,
            )

        # Update the profile picture if necessary
        if thalia_user.user.profile_photo != photo:
            thalia_user.user.profile_photo = photo
            thalia_user.user.save()

        # Fully authenticate the user
        login(request, thalia_user.user)

        # User login fully succeeded
        return True
