from rest_framework import serializers
from rest_framework.fields import CharField, FileField

from files.models.base import File
from files.models.requests import FileStorageRequest

# ------------------ #
# Request Serializer #
# ------------------ #

# Used for the 1st phase of a file upload:
# creates a file storage request and gives
# the frontend the necessary information for
# uploading to the desired storage.


class RequestSerializer(serializers.ModelSerializer):
    """
    Serializer that is meant to register a file
    request object creation

    ----

    **Contains** the additional fields:

    - ``storage_folder``: The folder where the file
      record should be stored

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    storage_folder = CharField(read_only=False)
    name = CharField(read_only=False)

    class Meta:
        model = FileStorageRequest
        fields = ("name", "type", "storage_folder")


# ----------------- #
# Upload Serializer #
# ----------------- #

# Used for the 2nd phase of uploading a file:
# In this case, the upload serializer only should
# allow for local file upload, as it catches a file
# storage request and makes a local file based on it.


class UploadSerializer(serializers.ModelSerializer):
    """
    Serializer that is meant to create a file object
    from a source file.

    ----

    **Contains** the additional fields:

    - ``request_id``: The id of the initial storage request
    - ``file``: The raw uploaded file

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    file = FileField(read_only=False)

    class Meta:
        model = File
        fields = ("file", "storage_key")


# ------------------- #
# Registry Serializer #
# ------------------- #


# Used for the 3rd phase of uploading a file:
# Using the recently created storage
# request as proof that the file has been properly
# stored in the preferred storage manager.


class RegistrySerializer(serializers.ModelSerializer):
    """
    Serializer that is meant to allow for file
    request retrieval in order to completely initialize
    a ``File`` model based on the direct-to-cloud upload.

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    class Meta:
        model = FileStorageRequest
        fields = ("id",)


# -------------------- #
# Retrieval Serializer #
# -------------------- #


# Used for retrieving a file from the
# storage, differentiates between files in local
# storage or cloud storage


class RetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer that is used when retrieving a File
    object. Only used for retrieving the file's important
    display fields.

    ----

    **Contains** the additional fields:

    - ``source``: The source of the file as an url

    ----

    The ``fields`` and ``read_only_fields`` are specified in
    the ``Meta`` subclass.
    """

    source = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ("source", "name", "type", "thumbnail", "is_compressed")
        read_only_fields = fields

    # ----------------- #
    # Additional Fields #
    # ----------------- #

    def get_source(self, instance):
        """
        Retrieves the source of the file regardless
        of storage.

        :param instance: The file instance
        :type instance: files.models.base.File

        :return: The file source as an url
        :rtype: str
        """

        return instance.url

    def get_thumbnail(self, instance):
        """
        Retrieves the source of the file's thumbnail
        regardless of storage.

        :param instance: The file instance
        :type instance: files.models.base.File

        :return: The file's thumbnail source as an url
        :rtype: str
        """

        return instance.thumbnail_url
