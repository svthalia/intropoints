from rest_framework.exceptions import NotFound


class TeamAPIUtilities:
    """
    Class that provides team API utilities, for
    easier standardization and access.

    ----

    **Provides** the functionality:

    - ``get_team_from_request``: Retrieves the team of the user in the request
    """

    @staticmethod
    def get_team_from_request(request):
        """
        Retrieves the team of the user in the request.

        ----

        :param request: The HTTP request that was made
        :type request: django.http.HttpRequest

        :return: The team instance
        :rtype: teams.models.Team
        """

        current_user = request.user
        team = current_user.teams.first()

        # Check if the user actually is part of a team
        if not team:
            raise NotFound("This user is not associated with any team!")
        # Otherwise, just return the team
        return team
