import json

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from users.models import UserPermissions

User = get_user_model()

# -------------------- #
# User proper creation #
# -------------------- #


class UserCreationTests(TestCase):
    """
    Tests whether user creation functions as intent and that
    is successful only for unique users.
    """

    def test_user_creation(self):
        """
        Tests that user creation is successful.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        created_user = get_user_model().objects.create(username="test")
        created_user.display_name = "display_test"
        created_user.profile_photo = "http://testserver/photo.jpg"
        created_user.save()

        stored_user = get_user_model().objects.get(username="test")

        self.assertEqual(created_user.display_name, stored_user.display_name)
        self.assertEqual(created_user.profile_photo, stored_user.profile_photo)

    def test_invalid_user_creation(self):
        with self.assertRaises(IntegrityError):
            """
            Tests whether two users cannot have the same username.

            ----

            :param: None

            :return: None
            :rtype: None
            """

            user1 = get_user_model().objects.create(username="test")
            user1.save()

            user2 = get_user_model().objects.create(username="test")
            user2.save()

    def test_same_name_user_creation(self):
        """
        Tests whether two users can have the same display name, but
        a different username.

        Should not throw any exception

        ----

        :param: None

        :return: None
        :rtype: None
        """

        user1 = get_user_model().objects.create(username="test1")
        user1.display_name = "display_test"
        user1.save()

        user2 = get_user_model().objects.create(username="test2")
        user2.display_name = "display_test"
        user2.save()

    def test_user_removal(self):
        with self.assertRaises(get_user_model().DoesNotExist):
            """
            Tests that after the user is removed, it is no longer present
            in the database.

            ----

            :param: None

            :return: None
            :rtype: None
            """

            created_user = get_user_model().objects.create(username="test")
            created_user.display_name = "display_test"
            created_user.profile_photo = "http://testserver/photo.jpg"
            created_user.save()

            get_user_model().objects.get(username="test").delete()
            get_user_model().objects.get(username="test")


# --------------- #
# User API checks #
# --------------- #


class UserAPITests(TestCase):
    """
    Tests whether the API endpoints for users is working
    normally, and that it cannot be taken advantage of.
    """

    def test_unauthenticated_api_retrieval(self):
        """
        Tests whether the API is unaccessible for unauthenticated
        client.

        ----

        :param: None

        :return: None
        :rtype: None
        """
        url = reverse("api:users:current_user")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_api_retrieval(self):
        """
        Tests whether the API is accessible for authenticated clients,
        and that it provides the right data.

        ----

        :param: None

        :return: None
        :rtype: None
        """
        url = reverse("api:users:current_user")

        self.user = get_user_model().objects.create_user(username="test", display_name="display_test", initials="")

        self.client.force_login(self.user)

        response = self.client.get(url)
        info = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(info["username"], self.user.display_name)

    def test_empty_api_retrieval(self):
        """
        Tests whether when retrieving a non-existent user from
        the API, the response is proper.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        url = reverse("api:users:current_user")

        self.user = get_user_model().objects.create_user(username="test", display_name="display_test", initials="")
        self.client.force_login(self.user)
        self.user.delete()

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ------------------- #
# User manager checks #
# ------------------- #


class UserManagerTests(TestCase):
    """Tests the custom user manager creation helpers."""

    def test_create_user_stores_fields(self):
        user = User.objects.create_user(username="alice", display_name="Alice", initials="AL")

        self.assertEqual(user.username, "alice")
        self.assertEqual(user.display_name, "Alice")
        self.assertEqual(user.initials, "AL")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_gets_participant_permission(self):
        user = User.objects.create_user(username="bob", display_name="Bob", initials="BO")

        self.assertTrue(user.user_permissions.filter(codename=UserPermissions.PARTICIPANT).exists())

    def test_create_superuser_flags(self):
        admin = User.objects.create_superuser(username="root")

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_username_is_unique(self):
        User.objects.create_user(username="dup", display_name="One", initials="ON")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="dup", display_name="Two", initials="TW")

    def test_display_name_can_repeat(self):
        User.objects.create_user(username="u1", display_name="Same", initials="SA")
        # Should not raise: only the username must be unique.
        User.objects.create_user(username="u2", display_name="Same", initials="SA")
