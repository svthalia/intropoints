from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

# ------------------------ #
# Authentication Utilities #
# ------------------------ #


class AuthUtils(TemplateView):
    """
    Encapsulate basic end-stage authentication
    utilities.

    ----

    **Provides** the functionality:

    - ``store_credentials``: Storing credentials in the client
    - ``create_access_cookie``: Creating a login session cookie
    """

    @staticmethod
    def store_credentials(request, response):
        """
        Pulls received oauth credentials and stores them in
        a session cookie inside the given response.

        ----

        :param request: The HTTP request that was made
        :return: HttpResponse

        :param response: The HTTP response in which to store the session cookie
        :return: HttpResponse

        :return: None
        :return: None
        """

        # Retrieve the necessary data
        access_token = request.GET.get("access_token")
        token_type = request.GET.get("token_type")
        scope = request.GET.get("scope")
        expires_in = request.GET.get("expires_in")

        # Set the authentication cookie
        response.set_cookie(
            key="loginSession",
            value=AuthUtils.create_access_cookie(access_token, token_type, scope),
            # The cookie expires in a week from being received;
            # this coincides with the event's duration.
            max_age=(int(expires_in) * 14 * 24),
            secure=settings.SECURE_COOKIES,
            samesite="Lax",
        )

    @staticmethod
    def create_access_cookie(access_token, token_type, scope):
        """
        Creates an access session cookie object from the give
        OAuth credentials.

        ----

        :param access_token: The user authorization token
        :type access_token: str

        :param token_type: The type of the authorization token
        :type token_type: str

        :param scope: The scope that the toke has access to
        :type scope: str

        ----

        :return: The login session cookie
        :rtype: str
        """

        # Store the cookie in the client
        access_cookie = {
            "token": access_token,
            "tokenType": token_type,
            "scope": scope.split("+"),
        }

        return access_cookie


# --------------------------- #
# Authentication cookie store #
# --------------------------- #


class AuthStoreView(TemplateView):
    """
    View that stores the retrieved OAuth credentials inside
    the client as a session cookie for easy retrieval for API use.
    """

    def get(self, request, **kwargs):
        """
        Retrieves the necessary credentials and redirects
        to the main page.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: Redirects to the given response with the session cookie set
        :rtype: HttpResponse
        """

        # Verify state stored before the request to protect against CSRF
        state_in_request = request.GET.get("state")
        state_in_session = request.session.get("state")
        if state_in_request != state_in_session:
            return HttpResponse(content="Invalid request!", status=502)

        response = redirect("/navigation")
        response.delete_cookie("state")
        response.delete_cookie("loginSession")
        AuthUtils.store_credentials(request, response)
        return response


# ------------------------------ #
# Authentication Bridge Callback #
# ------------------------------ #

# Mainly used to enforce backend handled
# authentication
#
# If this is skipped, then the frontend can
# pick on the authorization request


class AuthCallbackView(TemplateView):
    """
    View that is called at the end of the OAuth authentication process.
    Handles authenticating the user via storing the given credentials
    for easy retrieval from the frontend.

    Acts as a bridge before the storing process can take action.
    This bridge makes it possible for the parameters to be accessed by the
    backend.
    """

    # ------------------ #
    # Base Functionality #

    def get(self, request, **kwargs):
        """
        Simply calls the bridging page for processing the
        token information.

        :param request: HttpRequest
        :param kwargs: Dictionary

        :return: HttpResponse
        """

        return render(request, "login/auth.html")
