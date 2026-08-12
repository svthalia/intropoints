from django.db import models

from files.utils.validation import FileValidationUtilities

# -------------------- #
# Initial File Request #
# -------------------- #


class FileStorageRequest(models.Model):
    """
    Represents an in-progress direct-to-S3 request.

    This model exists so orphaned uploads (e.g. mid-upload crashes) can
    be cleaned up by the cleanup_orphaned_uploads() job:

    ----

    **Contains** the fields:

    - ``name``: the file's name
    - ``unique_name``: the file's unique name
    - ``type``: the file's MIME type
    - ``created_at``: the timestamp of the file's creation
    - ``finished_at``: the timestamp of the file's uploading procedure
    - ``presigned_data``: the presigned POST data used for the S3 upload
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    created_at = models.DateTimeField(
        help_text="The time the request was made",
        auto_now=True,
        null=False,
        blank=False,
    )
    """ The time the request was made at """

    finished_at = models.DateTimeField(
        help_text="The time the request was finished at", null=True, blank=False, default=None
    )
    """ The time the request was made at """

    storage_key = models.CharField(
        help_text="The key at which the file is stored",
        max_length=400,
        unique=True,
        null=False,
        blank=False,
        default="",
    )
    """ The unique storage key for the requested file """

    type = models.CharField(
        help_text="The MIME type of the file",
        max_length=50,
        validators=[FileValidationUtilities.validate_mime_type],
        null=False,
        blank=False,
        default="",
    )
    """ The MIME type of the file """

    presigned_data = models.JSONField(
        help_text="The presigned data that is used for direct-to-cloud upload", null=True, blank=True, default=None
    )
    """ The presigned data that is used for direct-to-cloud upload """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the file request to a string representation.
        This is done based on its name and type.

        ----

        :param: None

        :return: The string representation of the request
        :rtype: str
        """

        return f"File storage {self.id} ({self.type})"

    def save(self, *args, **kwargs):
        """
        Mainly overrides the main `save()` functionality in order
        to validate the stored file's MIME type, and to populate the
        required fields from:

        - The presigned data
        - The given source

        ----

        :param args: Positional arguments
        :type args: tuple

        :param kwargs: Dictionary arguments
        :type kwargs: dict

        :return: None
        """

        self.full_clean(exclude=["presigned_data", "finished_at", "created_at", "storage_key"])
        super().save(*args, **kwargs)


# ------------------- #
# Compression Request #
# ------------------- #


class CompressionRequest(models.Model):
    """
    Records that a compression job has been submitted for a File.
    Used by the cron job to know which files to poll for completion.
    Should be deleted once compression completes or fails.

    -----

    **Contains**: the fields:

    - ``file``: the file which to compress
    - ``created_at``: the time the request was made
    - ``retries``: the number of retry-attempts
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    file = models.OneToOneField(
        "files.File",
        on_delete=models.CASCADE,
        related_name="compression_request",
        help_text="The file to be compressed",
        null=False,
        blank=False,
        default=None,
    )
    """ The file to compress """

    created_at = models.DateTimeField(
        help_text="The time the request was made at", auto_now=True, null=False, blank=False
    )
    """ The time the request was made at """

    retries = models.PositiveIntegerField(help_text="Number of retry attempts", null=False, blank=False, default=0)
    """ The number of times the request was processed """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the compression request to a string representation.
        This is done based on its unique name.

        ----

        :param: None

        :return: The string representation of the request
        :rtype: str
        """

        return f"Compression requested for {self.file.unique_name}"


# ----------------- #
# Thumbnail Request #
# ----------------- #


class ThumbnailRequest(models.Model):
    """
    Records that a thumbnail job has been submitted for a File.
    Used by the cron job to know which files to poll for completion.
    Should be deleted once thumbnail generation completes or fails.

    -----

    **Contains**: the fields:

    - ``file``: the file which to compress
    - ``created_at``: the time the request was made
    - ``retries``: the number of retry-attempts
    """

    # --------------- #
    # Database Fields #
    # --------------- #

    file = models.OneToOneField(
        "files.File",
        on_delete=models.CASCADE,
        related_name="thumbnail_request",
        help_text="The file to be processed for a thumbnail",
        null=False,
        blank=False,
        default=None,
    )
    """ The file to create a thumbnail for """

    created_at = models.DateTimeField(
        help_text="The time the request was made at", auto_now=True, null=False, blank=False
    )
    """ The time the request was made at """

    retries = models.PositiveIntegerField(help_text="Number of retry attempts", null=False, blank=False, default=0)
    """ The number of times the request was processed """

    # ------------------ #
    # Base Functionality #
    # ------------------ #

    def __str__(self):
        """
        Converts the thumbnail request to a string representation.
        This is done based on its unique name.

        ----

        :param: None

        :return: The string representation of the request
        :rtype: str
        """

        return f"Thumbnail requested for {self.file.unique_name}"
