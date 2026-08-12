import mimetypes
import uuid
from pathlib import Path

from django.conf import settings

# ------------------------ #
# File Attribute Utilities #
# ------------------------ #


class FileAttributeUtilities:
    """
    Provides utility functions for retrieving file
    field attributes from the file's full name.

    ----

    **Provides** the functionality:

    - ``get_unique_file_name(...)``: Generates a unique file name
    - ``get_file_mime_type(...)``: Retrieve's a file's MIME type
    """

    @staticmethod
    def get_unique_file_name(full_file_name):
        """
        Converts the given full file name to a completely unique
        one by appending an ``UUID``.

        ----

        :param full_file_name: File name with extension
        :type full_file_name: str

        :return: The file's unique name
        :rtype: str
        """

        # This has a timestamp, so it's going to be
        # unique!
        random_name = f"{Path(full_file_name).stem}__{uuid.uuid7()}"

        return random_name

    @staticmethod
    def get_file_mime_type(full_file_name):
        """
        Retrieves the file type from the file's full file name,
        which includes its extension.

        ----

        :param full_file_name: File name with extension
        :type full_file_name: str

        :return: The file's MIME type
        :rtype: str
        """

        mime_type = mimetypes.guess_type(str(full_file_name))[0]
        return mime_type


# --------------------- #
# File Folder Utilities #
# --------------------- #


class FileFolderUtilities:
    """
    Provides folder retrieval functionality.

    ----

    **Provides** the functionality:

    - ``get_compression_folder(...)``: Retrieves the compression folder for file storage
    - ``get_thumbnail_folder(...)``: Retrieves the thumbnail folder for file storage
    """

    @staticmethod
    def get_compression_folder(file):
        """
        Retrieves the compression folder for the
        given file.

        ----

        :param file: The file instance
        :type file: files.models.base.File

        :return: The compression folder
        :rtype: str
        """

        return f"{settings.FILE_STORAGE_COMPRESSION_FOLDER}/{file.storage_folder}"

    @staticmethod
    def get_thumbnail_folder(file):
        """
        Retrieves the thumbnail folder for the
        given file.

        ----

        :param file: The file instance
        :type file: files.models.base.File

        :return: The thumbnail folder
        :rtype: str
        """

        return f"{settings.FILE_STORAGE_THUMBNAIL_FOLDER}/{file.storage_folder}"


# -------------------------- #
# File Storage Key Utilities #
# -------------------------- #


class FileStorageKeyUtilities:
    """
    Utility class for retrieving and generating
    base file storage keys.

    ----

    **Provides** the functionality:

    - ``get_storage_key(...)``: Generates a file's storage key from its metadata
    - ``get_compressed_storage_key(...)``: Retrieve's a file's compressed storage key
    - ``get_thumbnail_storage_key(...)``: Retrieve's a file's thumbnail storage key
    """

    @staticmethod
    def get_storage_key(storage_folder, name, file_suffix):
        """
        Retrieves the relative file location to the media
        storage folder.

        ----

        :param storage_folder: The folder in which to store the files
        :type storage_folder: str

        :param name: The file's name without extension
        :type name: str

        :param file_suffix: The file extension / suffix
        :type file_suffix: str

        :return: The file's full storage location
        :rtype: str
        """

        return f"{storage_folder}/{name}{file_suffix}"

    @staticmethod
    def get_compressed_storage_key(instance, full_file_name):
        """
        Retrieves the relative file compression location to the
        media storage folder.

        ----

        :param instance: The file instance
        :type instance: files.models.base.File

        :param full_file_name: The file name with extension
        :type full_file_name: str

        :return: The file's thumbnail storage location
        :rtype: str
        """

        file_suffix = ".zip"

        if instance.is_image:
            file_suffix = ".jpg"

        if instance.is_video:
            file_suffix = ".mp4"

        folder = FileFolderUtilities.get_compression_folder(instance)

        return f"{folder}/{instance.unique_name}{file_suffix}"

    @staticmethod
    def get_thumbnail_storage_key(instance, full_file_name):
        """
        Retrieves the relative file thumbnail location to the
        media storage folder.

        ----

        :param instance: The file instance
        :type instance: files.models.base.File

        :param full_file_name: The file name with extension
        :type full_file_name: str

        :return: The file's thumbnail storage location
        :rtype: str
        """

        folder = f"{FileFolderUtilities.get_thumbnail_folder(instance)}"

        return f"{folder}/{instance.unique_name}__thumbnail.0000000.jpg"


# --------------------- #
# File Upload Utilities #
# --------------------- #


class FileUploadUtilities:
    """
    Provides upload utilities for the base
    storage of a file.

    ----

    **Provides** the functionality:

    - ``get_base_upload_location(...)``: Retrieves the initial upload location for a file
    """

    @staticmethod
    def get_base_upload_location(instance, full_file_name):
        """
        Retrieves the path where the file should be uploaded
        locally.

        ----

        Mainly used for providing the function that computes the
        file exact location.

        And differentiates between compressed and raw files.

        ----

        :param instance: The file instance
        :type instance: files.models.base.File

        :param full_file_name: The full file name with extension
        :type full_file_name: str

        :return: The local upload path
        :rtype: str
        """

        # Handle compressed files
        storage_folder = instance.storage_folder
        if instance.is_compressed:
            storage_folder = FileFolderUtilities.get_compression_folder(instance)
        file_suffix = Path(instance.source.name).suffix

        return FileStorageKeyUtilities.get_storage_key(storage_folder, instance.unique_name, file_suffix)
