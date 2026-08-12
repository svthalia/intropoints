from pathlib import Path

from botocore.exceptions import ClientError
from django.conf import settings
from django.utils import timezone

from files.models.requests import CompressionRequest, ThumbnailRequest
from files.storage.aws.clients import AWSClientFactory
from files.utils.storage import FileStorageKeyUtilities

# --------------------- #
# AWS Storage utilities #
# --------------------- #


class AWSStorageUtilities:
    """
    Utility class that provides storage location
    functions.

    ----

    **Provides** the functionality:

    - ``get_aws_s3_key(...)``: Retrieves the s3 key for a file
    - ``get_aws_s3_compressed_key(...)``: Retrieves the s3 key for a compressed file
    - ``get_aws_s3_thumbnail_key(...)``: Retrieves the s3 key for a file's thumbnail
    """

    @staticmethod
    def get_aws_s3_key(**kwargs):
        """
        Retrieves the aws s3 key for based on a 'file'
        signature: it's relevant names and folders.

        This can be given in a few different ways:

        ----

        ``Raw`` arguments:
        - storage_folder
        - unique_name
        - file_suffix

        ----

        ``File`` arguments:
        - File object with source and destination

        ----

        ``FileStorageRequest`` args:
        - FileStorageRequest with source and destination

        ----

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: The S3 unique file storage key
        :rtype: str
        """

        # Handle first option
        storage_folder = kwargs.get("storage_folder")
        unique_name = kwargs.get("unique_name")
        file_suffix = kwargs.get("file_suffix")
        if storage_folder and unique_name and file_suffix:
            return FileStorageKeyUtilities.get_storage_key(storage_folder, unique_name, file_suffix)

        # Handle second option
        file = kwargs.get("file")
        if file:
            storage_folder = file.storage_folder
            unique_name = file.unique_name
            file_suffix = Path(file.source.name).suffix
            return FileStorageKeyUtilities.get_storage_key(storage_folder, unique_name, file_suffix)

        # Handle third option
        file_request = kwargs.get("file_request")
        if file_request:
            storage_folder = file_request.storage_folder
            unique_name = file_request.unique_name
            file_suffix = Path(file_request.source.name).suffix
            return FileStorageKeyUtilities.get_storage_key(storage_folder, unique_name, file_suffix)

        raise ValueError("No valid arguments passed!")

    @staticmethod
    def get_aws_s3_compressed_key(file):
        """
        Retrieves the compressed s3 key for a given file; this is where
        the compression for the file will live.

        The file extension is determined by the file's type.

        ----

        :param file: The file instance
        :type file: files.models.base.File

        :return: String
        """

        return FileStorageKeyUtilities.get_compressed_storage_key(file, file.source.name)

    @staticmethod
    def get_aws_s3_thumbnail_key(file):
        """
        Retrieves the thumbnail s3 key for a given file; this is where
        the thumbnail for the file will live.

        Thumbnails will always be compressed, so, for now they are stored
        in a ``.jpg`` format.

        ----

        :param file: The file instance
        :type file: files.models.base.File

        :return: The S3 unique thumbnail storage key
        :rtype: str
        """

        return FileStorageKeyUtilities.get_thumbnail_storage_key(file, file.source.name)


# -------------------- #
# AWS Upload Utilities #
# -------------------- #


class AWSUploadUtilities:
    """
    Utility class that provides functionality for
    direct-to-cloud upload / direct-from-cloud
    retrieval

    ----

    **Provides** the functionality:

    - ``generate_aws_upload_presigned_url(...)``: Creates a presigned url for file retrieval
    - ``generate_aws_storage_presigned_url(...)``: Creates a presigned url for file storage
    """

    @staticmethod
    def generate_aws_storage_presigned_url(storage_key, file_type):
        """
        Generate a presigned **POST** URL for direct s3 uploads (for
        file storage requests within the frontend).

        This allows the frontend to upload directly to S3.
        Presigned URLs are time-limited and path-scoped.

        :param storage_key: The unique file storage key
        :type storage_key: str

        :param file_type: The MIME type of the file
        :type file_type: str

        :return: The presigned URL with included data
        """

        client = AWSClientFactory.get_s3()

        # Dynamically prepare the URL fields, this makes
        # the ACL completely optional if not needed
        fields = {"Content-Type": file_type}
        conditions = [
            {"Content-Type": file_type},
            ["content-length-range", 1, settings.FILE_MAX_SIZE],
        ]
        if settings.AWS_DEFAULT_ACL is not None:
            fields["acl"] = settings.AWS_DEFAULT_ACL
            conditions.append({"acl": settings.AWS_DEFAULT_ACL})

        return client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=storage_key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=settings.AWS_PRESIGNED_EXPIRY,
        )

    @staticmethod
    def generate_aws_retrieve_presigned_url(storage_key):
        """
        Generate a presigned **GET** URL for direct s3 retrieval (for
        file retrieval requests within the frontend).

        This allows the frontend to retrieve directly from S3.
        Presigned URLs are time-limited and path-scoped.

        ----

        :param storage_key: The unique file storage key
        :type storage_key: str

        :return: The presigned URL with included data
        """

        client = AWSClientFactory.get_s3()

        return client.generate_presigned_url(
            "get_object", Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": storage_key}, ExpiresIn=3600
        )


# -------------- #
# Cron Utilities #
# -------------- #


class AWSPollingUtilities:
    """
    Utility class for polling job operations and S3 interaction.

    Handles common operations across cron jobs such as
    S3 object existence checking, source file deletion, and
    timeout management for failed jobs.

    ----

    **Provides** the constants:

    - ``PROCESSING_TIMEOUT_MINUTES``: The timeout for processing files
    - ``MAX_RETRIES``: The amount of retries before a request goes stale

    ----

    **Provides** the functionality:

    - ``handle_timeout(...)``: Handles timed out jobs
    - ``s3_object_exists(...)``: Checks if a file exists in S3
    """

    PROCESSING_TIMEOUT_MINUTES = 5
    """ Timeout for any file processing request """

    MAX_RETRIES = 3
    """ Maximum amount of retries before a request gets deleted """

    @staticmethod
    def s3_handle_timeout(timeout):
        """
        Handle timed-out compression/thumbnail jobs with retry logic.

        For jobs that have exceeded ``timeout``:

        - Increment retry counter
        - If max retries exceeded, delete the job request
        - Otherwise, reset the created_at timestamp to retry again

        ----

        :param timeout: The timeout to check against
        :type timeout: datetime.datetime

        :return: None
        :rtype: None
        """

        # Retrieve stale files
        stale_thumbnails = ThumbnailRequest.objects.filter(created_at__lt=timeout)
        stale_compressions = CompressionRequest.objects.filter(created_at__lt=timeout)

        # Increase the retries or abandon the job
        for job in stale_thumbnails:
            job.retries += 1

            if job.retries >= AWSPollingUtilities.MAX_RETRIES:
                job.delete()
            else:
                job.created_at = timezone.now()
                job.save(update_fields=["retries", "created_at"])

        for job in stale_compressions:
            job.retries += 1

            if job.retries >= AWSPollingUtilities.MAX_RETRIES:
                job.delete()
            else:
                job.created_at = timezone.now()
                job.save(update_fields=["retries", "created_at"])

    @staticmethod
    def s3_object_exists(aws_client, s3_key):
        """
        Check if an object exists in S3.

        Uses a ``HEAD`` request to check for object existence without
        downloading the object.

        ----

        :param aws_client: An AWS client for requests
        :type aws_client: botocore3.client.BaseClient

        :param s3_key: The unique file key
        :type s3_key: str

        :return: Whether the object exists or not
        :rtype: bool
        """

        # This should generally be true, and it's alright
        # to handle this through exceptions, since that represents
        # data integrity faults.
        try:
            aws_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
            return True
        except ClientError as Error:
            if Error.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return False
            raise Error
