from pathlib import Path

from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files.api.serializers import RegistrySerializer, RequestSerializer, UploadSerializer
from files.models.base import File
from files.models.requests import FileStorageRequest
from files.storage.local.utils import LocalStorageUtilities, LocalUploadUtilities
from files.utils.storage import FileAttributeUtilities

# -------------------- #
# Storage Request View #
# -------------------- #


# File upload step 1:
#
# Make a request towards the storage manager


class RequestLocalStorageAPIView(APIView):
    """
    Views that handles creating a storage request from
    the file's metadata: ``full_name`` and ``type``.
    """

    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def post(self, request, *args, **kwargs):
        """
        Retrieves the file's metadata from the **POST** request and
        creates a **local storage key** and **storage request** from
        """

        # Validate the
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the file's metadata
        file_name = request.data.get("name")
        file_type = request.data.get("type")
        storage_folder = request.data.get("storage_folder")

        # Create the unique storage identifier
        unique_file_name = FileAttributeUtilities.get_unique_file_name(file_name)
        local_key = LocalStorageUtilities.get_local_key(
            storage_folder=storage_folder,
            unique_name=unique_file_name,
            file_suffix=Path(file_name).suffix,
        )

        # Retrieve the local presigned url
        presigned_data = LocalUploadUtilities.generate_local_presigned_url(local_key)

        # Make a file storage request
        file_storage_request = FileStorageRequest.objects.create(
            storage_key=local_key,
            type=file_type,
        )

        # Inform the client about the presigned data and the
        # storage request's id
        return Response(
            data={"id": file_storage_request.id, "presigned_data": presigned_data},
            status=status.HTTP_201_CREATED,
        )


# ---------------------- #
# Upload to Storage View #
# ---------------------- #


# File upload step 2:
#
# Upload directly to the destination


class UploadToLocalStorageAPIView(APIView):
    """
    Views that handles uploading a file to the backend's local
    storage, and registering a ``File`` model that is linked to
    the stored file.
    """

    serializer_class = UploadSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = DjangoFilterBackend

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def post(self, request, *args, **kwargs):
        """
        Retrieves the source file and creates a database
        object that is linked with it, containing its metadata.
        """

        # Validating the raw data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieving the file source and its local key
        file_source = request.data.get("file")
        encoded_file_storage_key = request.data.get("storage_key")

        # Check the signature for the payload
        try:
            signer = TimestampSigner()
            file_storage_key = signer.unsign(encoded_file_storage_key, max_age=1800)
        except SignatureExpired:
            return Response({"detail": "The signature expired"})
        except BadSignature:
            return Response({"detail": "The signature was invalid"})

        file = File.from_storage_key(storage_key=file_storage_key)
        file.source = file_source
        file.save(update_fields=["source"])

        # Return the file id if needed by the client
        return Response(
            {"detail": "File successfully created."},
            status=status.HTTP_201_CREATED,
        )


# --------------------- #
# Register Storage View #
# --------------------- #


# File upload step 3:
#
# Register the successful upload locally


class RegisterLocalStorageAPIView(APIView):
    """
    View that handles registering the file upload locally.
    Since this is a local handler, the file was already uploaded,
    so it only needs to validate that the request has finished,
    and delete its database counterpart.
    """

    serializer_class = RegistrySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def post(self, request, *args, **kwargs):
        """
        Tries to retrieve the request linked by the **POST**ed
        ID, if it succeeds, it acknowledges the request and deletes it.
        """

        # Validate the raw data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Retrieve the request and delete it
        file_storage_request_id = request.data.get("id")
        file_storage_request = FileStorageRequest.objects.get(id=file_storage_request_id)
        file = File.objects.get(storage_key=file_storage_request.storage_key)

        file_storage_request.delete()
        return Response(
            {"detail": "File successfully registered.", "id": file.id},
            status=status.HTTP_200_OK,
        )
