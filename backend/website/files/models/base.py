import re
import uuid
from pathlib import Path

from django.conf import settings
from django.db import models

# Might be nice to separate this
from files.storage.aws.utils import AWSUploadUtilities
from files.utils.storage import FileAttributeUtilities, FileStorageKeyUtilities, FileUploadUtilities
from files.utils.validation import FileValidationUtilities

# ---------- #
# File Model #
# ---------- #


class File(models.Model):
    """
    Class that represents a stored file within the backend
    system. The file can be of any supported format.

    ----

    **Contains**:

    - ``id``: The model's id in a ``UUID7`` format
    - ``source``: The source of the file (raw object)
    - ``name``: The file's original name
    - ``type`` The file's MIME type

    Important:

    - ``storage_folder``: The file's storage folder - which NEEDS
      to be overridden when saving the file using a source
      in order to properly specify the path;
    - ``storage_key``: The unique storage key of the file (full relative path)
    - ``storage_type``: The storage type that was used to store the file
    """

    # --------------- #
    # Storage Options #
    # --------------- #

    # Required for dynamically determining the upload
    # folder location;
    #
    # This should be overridden when a model introduces a
    # foreign key to the File model
    storage_folder = models.CharField(
        help_text="The storage folder in which the file sits", max_length=300, null=False, blank=False, default="files/"
    )
    """ The storage folder where the file is stored """

    storage_key = models.CharField(
        help_text="The storage key of the file", unique=True, max_length=400, null=False, blank=False, default=""
    )
    """ The unique key for file retrieval and storage """

    storage_type = models.CharField(
        help_text="The storage type that was used for the file",
        max_length=50,
        null=False,
        blank=False,
        default=settings.LOCAL_STORAGE,
    )
    """ The type of the storage used for saving the file """

    # --------------- #
    # Database Fields #
    # --------------- #

    id = models.UUIDField(
        help_text="The id of the file", primary_key=True, null=False, blank=False, default=uuid.uuid7, editable=False
    )
    """ The id of the file in a uuid7 format for randomization and efficiency """

    name = models.CharField(
        help_text="The file's original name",
        max_length=300,
        null=False,
        blank=False,
        default="",
    )
    """ The name of the file """

    unique_name = models.CharField(
        help_text="The file's unique name",
        max_length=300,
        null=False,
        blank=False,
        default="",
    )
    """ The unique name of the file used for storage"""

    type = models.CharField(
        help_text="The file's MIME type",
        max_length=50,
        validators=[FileValidationUtilities.validate_mime_type],
        null=False,
        blank=True,
        default="",
    )
    """ The MIME type of the file """

    # ------------------ #
    # Storage Components #
    # ------------------ #

    source = models.FileField(
        help_text="The raw source of the file",
        upload_to=FileUploadUtilities.get_base_upload_location,
        max_length=400,
        null=True,
        blank=True,
        default=None,
    )
    """ The actual raw source file """

    thumbnail = models.FileField(
        help_text="The raw thumbnail of the file",
        upload_to=FileStorageKeyUtilities.get_thumbnail_storage_key,
        max_length=400,
        null=True,
        blank=True,
        default=None,
    )
    """ The thumbnail of the file if it exists """

    is_compressed = models.BooleanField(
        help_text="Whether the file is compressed or not",
        null=False,
        blank=True,
        default=False,
    )
    """ Whether the file is compressed or not """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the file object to a string based on its
        name and type.

        ----

        :param: None

        :return: The string representation of the file
        :rtype: str
        """

        return f"File {self.name} ({self.type})"

    def save(self, *args, **kwargs):
        """
        Overrides the main ``save(...)`` functionality in order to
        validate the mime type in the process.

        ----

        :param args: Positional args
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        self.full_clean(exclude=["storage_folder", "storage_key", "source", "name", "unique_name", "thumbnail"])
        super().save(*args, **kwargs)

    # -------------- #
    # File Factories #
    # -------------- #

    @staticmethod
    def from_storage_key(storage_key):
        """
        Creates and saves a file object with its fields fully
        initialized from the given storage key and storage
        type

        ----

        :param storage_key: The unique storage key where the physical
        file is stored
        :type storage_type: str

        :param storage_type: The type if the storage that was used
        :type storage_type: str

        :return: The unsaved file instance
        :rtype: File
        """

        full_unique_file_name = Path(storage_key).name

        file = File()
        file.storage_type = settings.FILE_UPLOAD_STORAGE
        file.storage_key = storage_key
        file.storage_folder = Path(storage_key).parent
        file.source = storage_key
        file.unique_name = Path(full_unique_file_name).stem
        file.name = file.unique_name.split("__")[0]
        file.type = FileAttributeUtilities.get_file_mime_type(Path(storage_key).name)
        file.save()

        return file

    @staticmethod
    def from_source(source, storage_folder):
        """
        Creates and saves a file object with its fields fully
        initialized from the given source and storage
        type

        ----

        :param source: The source object that represents the stored file
        :type source: django.core.files.File

        :param storage_folder: The storage folder where the file is
        :type storage_folder: str

        :return: The saved file instance
        :rtype: File
        """

        full_file_name = Path(source.name).name

        safe_name = re.sub(r"\s+", "_", full_file_name)
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", safe_name)

        source.name = safe_name
        full_file_name = safe_name

        file = File()
        file.source = source
        file.storage_type = settings.FILE_UPLOAD_STORAGE
        file.storage_folder = storage_folder

        file.unique_name = FileAttributeUtilities.get_unique_file_name(full_file_name)
        file.name = Path(full_file_name).stem
        file.storage_key = FileStorageKeyUtilities.get_storage_key(
            file.storage_folder, file.unique_name, Path(full_file_name).suffix
        )
        file.type = FileAttributeUtilities.get_file_mime_type(full_file_name)
        file.save()

        return file

    # --------------------- #
    # Additional Properties #
    # --------------------- #

    @property
    def has_thumbnail(self):
        """
        Return True if a thumbnail has been generated
        for this file.

        ----

        :param: None

        :return: Whether the file has a thumbnail
        :rtype: bool
        """

        return bool(self.thumbnail)

    @property
    def is_video(self):
        """
        Whether the file is a video type.

        ----

        :return: Whether the file is a video type
        :rtype: bool
        """

        return self.type.startswith("video")

    @property
    def is_image(self):
        """
        Whether the file is an image type.

        ----

        :return: Whether the file is a image type
        :rtype: bool
        """

        return self.type.startswith("image")

    # -------------------- #
    # Retrieval Properties #
    # -------------------- #

    @property
    def url(self):
        """
        Retrieves the file url for accessing outside
        the backed.

        ----

        :param: None

        :return: The file access url
        :rtype: str
        """

        if self.storage_type == settings.LOCAL_STORAGE:
            return f"{settings.HOST_BASE_URI}media/{self.storage_key}"

        if self.storage_type == settings.S3_STORAGE:
            return AWSUploadUtilities.generate_aws_retrieve_presigned_url(self.storage_key)

        # How did we even get here?
        return ""

    @property
    def thumbnail_url(self):
        """
        Retrieves the file's thumbnail url for accessing outside
        the backed.

        ----

        :param: None

        :return: The thumbnail's access url
        :rtype: str
        """

        if self.has_thumbnail and self.storage_type == settings.LOCAL_STORAGE:
            return f"{settings.HOST_BASE_URI}media/{self.thumbnail.name}"

        if self.has_thumbnail and self.storage_type == settings.S3_STORAGE:
            return AWSUploadUtilities.generate_aws_retrieve_presigned_url(self.thumbnail.name)

        # How did we even get here?
        return ""
