from django.contrib.auth import logout
from django.http import HttpResponse  # noqa: F401
from django.shortcuts import redirect
from django.views.generic import TemplateView

# ----------- #
# Logout View #
# ----------- #


class LogoutView(TemplateView):
    """
    Logout view for processing user logout for
    the backend.

    Simply logs out the user and redirects to home.
    """

    def get(self, request, **kwargs):
        """
        Access the logout view if still registered, otherwise
        redirects to the previous request - or to  home.

        Otherwise, simply logs out the user from the backend.

        ----

        :param request: The HTTP request that was made
        :type request: HttpRequest

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: A redirect to the root page
        :rtype: HttpResponse
        """

        # If not a valid logout request, abort.
        next_url = request.GET.get("next", "/")
        if not request.user.is_authenticated:
            # Check if there was a previous request
            # to begin with
            if next_url:
                return redirect(next_url)
            return redirect("/")

        # Logout the user and redirect to home.
        logout(request)
        response = redirect("/")
        response.delete_cookie(key="loginSession", path="/", domain=None, samesite="Lax")
        return response
