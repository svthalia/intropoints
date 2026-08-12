from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Permission
from django.db import models

# ------------------- #
# Custom User Manager #
# ------------------- #


class UserManager(BaseUserManager):
    """
    User manager class that acts as a custom factory
    for defining user creation in compliance with django's
    requirements.

    ----

    **Defines** how to create:

    - users
    - superusers
    """

    def _init_user_(self, username, display_name, initials, **kwargs):
        """
        Stores a user inside the database.

        ----

        :param username: The username of the user
        :type username: str

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: The stored user
        :rtype: User
        """

        # Make sure that there is always a display name
        # provided, even if the given one is empty
        if not display_name:
            display_name = username

        # Create the user model
        user = self.model(username=username, display_name=display_name, initials=initials, **kwargs)

        # Essentially, this still enables admin users to
        # have a password, while normal users are unable to
        if "password" in kwargs:
            user.set_password(kwargs.pop("password"))
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        # Set basic permissions
        user.user_permissions.add(Permission.objects.get(codename=UserPermissions.PARTICIPANT))

        return user

    def create_user(self, username, display_name, initials, **kwargs):
        """
        Creates a basic application user.

        ----

        :param username: The username of the user
        :type username: str

        :param display_name: The display name of the user
        :type display_name: str

        :param initials: Initials of the user (E. X.)
        :type initials: str

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: The stored user
        :rtype: User
        """

        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)

        return self._init_user_(username=username, display_name=display_name, initials=initials, **kwargs)

    def create_superuser(self, username, **kwargs):
        """
        Creates a superuser, which is marked as:

        - **Staff**
        - **Superuser**

        ----

        Automatically resolves initials and display
        name requirements.

        ----

        :param username: The username of the user
        :type username: str

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: The stored user
        :rtype: User
        """

        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)

        return self._init_user_(username=username, display_name=f"Admin {username}", initials=username[0], **kwargs)


# ---------------- #
# User Permissions #
# ---------------- #


class UserPermissions:
    """
    General class that describes the different custom
    user permissions used for the website.

    ----

    **Defines** the permissions:

    - ``PARTICIPANT``: Default user access
    - ``MENTOR``: **Not used yet**
    - ``IC_MEMBER``: Higher privileges:
        - Grading submissions
        - Accepting submissions
        - Making challenges visible
        - Rejecting submissions
    """

    PARTICIPANT = "participant"
    """ Represents a basic participant """

    MENTOR = "mentor"
    """ Represents and introduction mentor"""

    IC_MEMBER = "ic_member"
    """ Represents and introduction committee member"""


# ---------- #
# User Model #
# ---------- #


class User(AbstractUser):
    """
    Base user class for the entire application.
    Represents the user of the environment.

    ----

    The user permissions are being stored and defined
    inside the ``Meta`` class.

    ----

    **Contains** the fields:

    - ``username``: The internal username
    - ``initials``: The user's initials
    - ``display_name``: The user's display name
    - ``profile_photo``: The user's profile photo's url
    """

    # --------------- #
    # Database fields #
    # --------------- #

    username = models.CharField(
        help_text="The internal username",
        max_length=200,
        unique=True,
        null=False,
        blank=True,
        default="",
    )
    """ The internally stored username """

    initials = models.CharField(
        help_text="The user's initials",
        max_length=10,
        null=False,
        blank=False,
        default="",
    )
    """ The user's initials """

    display_name = models.CharField(
        help_text="The user's display name",
        max_length=200,
        null=False,
        blank=False,
        default="",
    )
    """ The user's display name """

    profile_photo = models.URLField(help_text="The user's profile photo url", null=False, blank=True, default="")
    """ The user's profile photo url """

    # -------------- #
    # Custom Manager #
    # -------------- #

    objects = UserManager()

    # --------------- #
    # Base Meta Class #
    # --------------- #

    class Meta:
        permissions = (
            (UserPermissions.PARTICIPANT, "Intro participant"),
            (UserPermissions.MENTOR, "Intro mentor"),
            (UserPermissions.IC_MEMBER, "Introduction Committee member"),
        )

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the user to a string object based on its
        display name. If the display name is not provided,
        then it defaults to the internal username.

        ----

        :param: None

        :return: The string representation of the user
        :rtype: str
        """

        if self.display_name:
            return self.display_name
        return self.username

    # ------------------------ #
    # Additional Functionality #
    # ------------------------ #

    def is_mentor(self):
        """
        Checks whether the user is a mentor or not

        ----

        :param: None

        :return: Whether the user is a mentor or not
        :rtype: bool
        """
        return self.has_perm(UserPermissions.MENTOR)

    def is_ic_member(self):
        """
        Checks whether the user is a IC member or not;

        ----

        :param: None

        :return: Whether the user is an IC member or not
        :rtype: bool
        """

        return self.has_perm(UserPermissions.IC_MEMBER)
