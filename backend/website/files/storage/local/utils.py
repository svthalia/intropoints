from django.conf import settings
from django.core.signing import TimestampSigner

from files.utils.storage import FileStorageKeyUtilities

# ----------------------- #
# Local Storage Utilities #
# ----------------------- #


class LocalStorageUtilities:
    """
    Utility class that provides storage location
    functions.

    ----

    **Provides** the functionality:

    - ``get_local_s3_key(...)``: Retrieves the local key for a file
    """

    @staticmethod
    def get_local_key(storage_folder, unique_name, file_suffix):
        """
        Generates a local storage key based on a file's / storage request's
        metadata.

        ----

        :param storage_folder: The folder where the file should be stored
        :type storage_folder: str

        :param unique_name: The file's unique name
        :type unique_name: str

        :param file_suffix: The file extension / suffix
        :type file_suffix: str

        :return: The local storage key
        :rtype: str
        """

        return FileStorageKeyUtilities.get_storage_key(storage_folder, unique_name, file_suffix)


# ---------------------- #
# Local Upload Utilities #
# ---------------------- #


class LocalUploadUtilities:
    """
    Utility class that provides functionality for
    direct-to-cloud upload / direct-from-cloud
    retrieval

    ----

    **Provides** the functionality:

    - ``generate_local_storage_presigned_url(...)``: Creates a presigned url for file storage
    """

    @staticmethod
    def generate_local_presigned_url(storage_key):
        """
        Generates a presigned URL based on the local storage key
        of the file request / file.

        ----

        :param storage_key: The file storage key
        :type storage_key: str

        :return: The presigned URL data
        :rtype: dict
        """

        signer = TimestampSigner()
        encode_storage_key = signer.sign(storage_key)

        data = {
            "url": f"{settings.HOST_BASE_URI}api/files/upload-to-storage/",
            "fields": {
                "storage_key": encode_storage_key,
            },
        }

        return data
