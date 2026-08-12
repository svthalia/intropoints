from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from users.models import (
    User,  # noqa
    UserPermissions,
)


class RetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer that includes all possible user
    fields for proper single display.

    ----

    **Additional** fields:

    - ``username``: The username that is dynamically chosen
    - ``permissions``: The user's **RELEVANT** permissions

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    username = serializers.CharField(source="__str__", read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "profile_photo",
            "initials",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "profile_photo",
            "initials",
            "permissions",
        ]

    # ---------------------------- #
    # Additional serializer fields #
    # ---------------------------- #

    @extend_schema_field(serializers.ListField)
    def get_permissions(self, instance):
        """
        Retrieves all user permissions and stores
        them in a list. These are only custom user
        permissions relevant to the website.

        ----

        :param instance: The user instance
        :type instance: User

        :return: The list of user permissions
        :rtype: list
        """

        # Only consider relevant user permissions within
        # the application's scope
        return [
            x
            for x in instance.get_all_permissions()
            if x
            in (
                f"users.{UserPermissions.PARTICIPANT}",
                f"users.{UserPermissions.MENTOR}",
                f"users.{UserPermissions.IC_MEMBER}",
            )
        ]
