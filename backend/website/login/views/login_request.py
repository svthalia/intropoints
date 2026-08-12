import base64
import hashlib

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views.generic import TemplateView
from oauthlib.oauth2 import WebApplicationClient

from login.models import AuthenticationRequest

# ---------------------- #
# Abstract Login Classes #
# ---------------------- #


class LoginView(TemplateView):
    """
    General View for handling user login through
    self-defined means.

    On retrieving the view it calls the '_auth_user_' function
    which should be implemented by any subclass for proper authorization.

    ----

    **Abstract** methods:

    - ``_auth_user_(...)``: Authenticates the user based on the desired method
    """

    def get(self, request, **kwargs):
        """
        Accesses the login view if not-yet-registered.
        Prepares for OAuth login / registration in the above case.

        If already registered, redirects to the Home URL.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: Redirect either to authentication or to home
        :rtype: HttpResponse
        """

        # Check if the user is already authenticated,
        # otherwise redirect to the base page
        if request.user.is_authenticated:
            return redirect("/navigation")
        return self._auth_user_(request)

    def _auth_user_(self, request):
        """
        **!! Virtual method, implement it in subclass !!**

        ----

        Authenticates the user based on the desired method.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :return: A proper redirect to the authentication handler
        :rtype: HttpResponse
        """


# ---------------------- #
# Concrete Login Classes #
# ---------------------- #


class ThaliaLoginView(LoginView):
    """
    Login view that handles authorization through
    the Thalia API.
    """

    # ------------------------ #
    # Overridden Functionality #
    # ------------------------ #

    def _auth_user_(self, request):
        """
        Makes a request for OAuth authorization through
        the Thalia API.

        Redirects the user towards the Thalia login endpoint
        if it succeeds.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :return: Redirect to Thalia login
        :rtype: HttpResponse
        """

        authentication_request = AuthenticationRequest.objects.create()
        client = WebApplicationClient(client_id=settings.THALIA_API_OAUTH_CLIENT_ID)

        code_verifier = authentication_request.challenge
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")

        authorization_url = client.prepare_request_uri(
            # Thalia OAuth endpoint access
            f"{settings.THALIA_API_BASE_URI}{settings.THALIA_API_AUTHORIZATION_ENDPOINT}",
            # Callback for Thalia auth
            redirect_uri=settings.THALIA_API_OAUTH_REDIRECT_URI
            + "?"
            + urlencode({"next": request.GET.get("next") or ""}),
            # Authentication challenge
            code_challenge=code_challenge,
            # Challenge verification method
            code_challenge_method="S256",
            # Authentication state / id
            state=authentication_request.state,
            # Limit the scope of the redirect to reading the profile
            scope=["profile:read"],
        )

        # Ask for the HTTP response from the Thalia API, and store
        # the Authentication state / id as a cookie
        response = HttpResponseRedirect(authorization_url)
        response.set_cookie("state", authentication_request.state, max_age=300)

        return response
