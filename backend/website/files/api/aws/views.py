from pathlib import Path

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files.api.serializers import RegistrySerializer, RequestSerializer
from files.models.base import File
from files.models.requests import FileStorageRequest
from files.storage.aws.compression import ImageCompressionJob, VideoCompressionJob
from files.storage.aws.utils import AWSStorageUtilities, AWSUploadUtilities
from files.utils.storage import FileAttributeUtilities

# -------------------- #
# Storage Request View #
# -------------------- #

# File upload step 1:
#
# Make a request towards the storage manager


class RequestAWSStorageAPIView(APIView):
    """
    View that creates a file storage request towards
    the AWS S3 instance, and creates a ``presigned_data``
    component that the frontend can use in order to upload
    directly to the S3 instance.
    """

    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = DjangoFilterBackend

    def post(self, request, *args, **kwargs):
        """
        Retrieves a file's metadata, and creates a file storage request
        towards the AWS S3 instance.

        ----

        The storage folder needs to be in the allowed types:

        - ``submissions``
        - ``challenges``
        - ``files``

        ----

        This is done with a ``presigned_data`` component that allows the
        frontend to upload directly to the S3 instance.
        """

        # Validate the raw data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the file's metadata
        file_name = request.data.get("name")
        file_type = request.data.get("type")
        storage_folder = request.data.get("storage_folder")

        if storage_folder not in settings.ALLOWED_FILE_STORAGE_FOLDERS:
            raise ValueError("The storage folder is not supported!")

        # Create the unique file keys
        unique_file_name = FileAttributeUtilities.get_unique_file_name(file_name)
        s3_key = AWSStorageUtilities.get_aws_s3_key(
            storage_folder=storage_folder,
            unique_name=unique_file_name,
            file_suffix=Path(file_name).suffix,
        )

        # Make the storage request and the presigned data component
        presigned_data = AWSUploadUtilities.generate_aws_storage_presigned_url(s3_key, file_type)
        file_storage_request = FileStorageRequest.objects.create(
            type=file_type,
            storage_key=s3_key,
        )

        # Give the client the request id for verification and
        # the presigned data for upload
        return Response(
            {"detail": "Storage request made", "id": file_storage_request.id, "presigned_data": presigned_data},
            status=status.HTTP_201_CREATED,
        )


# --------------------- #
# Register Storage View #
# --------------------- #


# File upload step 3:
#
# Register the successful upload locally


class RegisterAWSStorageAPIView(APIView):
    """
    View that creates a file database instance based
    on the information from the file request that succeeded
    towards the AWS S3 instance.

    ----

    This file inherits all the information that is stored
    within the S3 instance, apart from the source.
    """

    serializer_class = RegistrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = DjangoFilterBackend

    def post(self, request, *args, **kwargs):
        """
        Retrieves a file request based on the given id and
        creates a file database object from its information.

        ----

        This newly created file will inherit the metadata of
        the request: ``name``, ``unique_name``...
        """

        # Validate the raw data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the original request
        file_storage_request_id = request.data.get("id")
        file_storage_request = FileStorageRequest.objects.get(id=file_storage_request_id)

        # Create the file from the given request
        file = File.from_storage_key(storage_key=file_storage_request.storage_key)

        # Trigger file processing after the successful
        # upload
        self._trigger_processing_(file)

        # Notify the client and give them the file id if needed
        return Response(
            data={"detail": "File successfully registered & processing started", "id": file.id},
            status=status.HTTP_201_CREATED,
        )

    # ---------------------- #
    # Internal Functionality #
    # ---------------------- #

    def _trigger_processing_(self, file):
        """
        Triggers compression and thumbnail processing via
        the scheduler for the given file.

        ----

        :param file: The file to process
        :type file: File

        :return: None
        :rtype: None
        """

        if file.is_video:
            VideoCompressionJob(file)
        elif file.is_image:
            ImageCompressionJob(file)
