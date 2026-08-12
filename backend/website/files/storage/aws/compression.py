import json

from django.conf import settings

from files.models.requests import CompressionRequest, ThumbnailRequest
from files.storage.aws.clients import AWSClientFactory
from files.utils.storage import FileFolderUtilities

# --------------------- #
# Compression Interface #
# --------------------- #


# Base abstract method for representing compression jobs
# within the system


class CompressionJob:
    """
    Base class that defines a compression job.

    Only defines abstract functionality and should
    be inherited for specific compression jobs.

    Requires the cloud storage url in order to be
    initialized properly.

    Abstract Methods:
        - _compress()
    """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __init__(self, file):
        """
        Initialize a CompressionJob object. This causes it
        to immediately start its compression requests:

        - File compression request
        - Thumbnail compression request

        ----

        :param file: The file instance
        :type file: files.models.base.File

        :return: CompressionJob
        """

        CompressionRequest.objects.create(file=file)
        ThumbnailRequest.objects.create(file=file)

        self._compress(file)
        return

    # ---------------------- #
    # Abstract Functionality #
    # ---------------------- #

    def _compress(self, file):
        """
        **!! ABSTRACT METHOD !!**

        ----

        Compresses the file at the given url according to the
        object's compression rules (video, image, etc.).

        ----

        :param: file: The file instance
        :type file: files.models.base.File

        :return: The job response object
        :rtype: dict
        """

        raise NotImplementedError()


# ----------------------- #
# Video Compression Class #
# ----------------------- #


class VideoCompressionJob(CompressionJob):
    """
    Represents a video compression job. On initialization, automatically
    requests an asynchronous compression job.
    """

    def _compress(self, file):
        """
        Submit a MediaConvert job to compress a video file.

        Initiates an asynchronous job that compresses the video at the
        given s3 key using the configured MediaConvert job template and role.

        ----

        :param: file: The file instance
        :type file: files.models.base.File

        :return: The job response object
        :rtype: dict
        """

        client = AWSClientFactory.get_mediaconvert()

        # Retrieve the file's unique storage options
        s3_key = file.storage_key

        # Prepare the file IO directories and s3 keys
        file_input_url = f"s3://{settings.AWS_STORAGE_BUCKET_NAME}/{s3_key}"
        compression_output_directory = (
            f"s3://{settings.AWS_STORAGE_BUCKET_NAME}/{FileFolderUtilities.get_compression_folder(file)}/"
        )
        thumbnail_output_directory = (
            f"s3://{settings.AWS_STORAGE_BUCKET_NAME}/{FileFolderUtilities.get_thumbnail_folder(file)}/"
        )

        # Create a job based on the previously set up
        # AWS MediaConvert template
        return client.create_job(
            JobTemplate=settings.AWS_MEDIACONVERT_TEMPLATE_NAME,
            Role=settings.AWS_MEDIACONVERT_ROLE_ARN,
            Settings={
                "Inputs": [{"FileInput": file_input_url}],
                "OutputGroups": [
                    {
                        "Name": "File Group",
                        "OutputGroupSettings": {
                            "Type": "FILE_GROUP_SETTINGS",
                            "FileGroupSettings": {"Destination": compression_output_directory},
                        },
                    },
                    {
                        "Name": "Thumbnails",
                        "OutputGroupSettings": {
                            "Type": "FILE_GROUP_SETTINGS",
                            "FileGroupSettings": {"Destination": thumbnail_output_directory},
                        },
                        "Outputs": [
                            {
                                "ContainerSettings": {"Container": "RAW"},
                                "VideoDescription": {
                                    "CodecSettings": {
                                        "Codec": "FRAME_CAPTURE",
                                        "FrameCaptureSettings": {
                                            "FramerateNumerator": 1,
                                            "FramerateDenominator": 5,
                                            "MaxCaptures": 5,
                                        },
                                    }
                                },
                                "NameModifier": "__thumbnail",
                            }
                        ],
                    },
                ],
            },
        )


# ----------------------- #
# Image Compression Class #
# ----------------------- #


class ImageCompressionJob(CompressionJob):
    """
    Represents an image compression job. On initialization,
    automatically requests an asynchronous compression job.
    """

    def _compress(self, file):
        """
        Invoke the image-compression Lambda for the given S3 URL.

        Triggers an asynchronous Lambda function to compress the
        image at the given s3 key. The Lambda function handles the
        compression and updates the file.

        ----

        :param: file: The file instance
        :type file: files.models.base.File

        :return: The job response object
        :rtype: dict
        """

        client = AWSClientFactory.get_lambda()
        payload_data = json.dumps(
            {
                "bucket_name": settings.AWS_STORAGE_BUCKET_NAME,
                "file_name": file.storage_key,
                "compression_folder": f"{FileFolderUtilities.get_compression_folder(file)}/",
                "thumbnail_folder": f"{FileFolderUtilities.get_thumbnail_folder(file)}/",
            }
        )

        return client.invoke(
            FunctionName=settings.AWS_IMAGE_COMPRESSION_FUNCTION_NAME,
            InvocationType="Event",
            Payload=payload_data.encode("utf-8"),
        )
