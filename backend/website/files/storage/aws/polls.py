from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from files.models.requests import CompressionRequest, FileStorageRequest, ThumbnailRequest
from files.storage.aws.clients import AWSClientFactory
from files.storage.aws.utils import AWSPollingUtilities, AWSStorageUtilities
from files.utils.deletion import FileDeletionUtilities

# --------------------- #
# Polling Functionality #
# --------------------- #


class PollS3:
    """
    Cron job service for polling S3 and updating File records.

    Periodically checks S3 for completed compression and thumbnail jobs,
    updates File records when jobs complete, and handles timeouts with
    retry logic for failed operations.

    ----

    **Provides** the functionality:

    - ``get_compressed_files(...)``: Polling for completed video/photo compression
    - ``get_thumbnail_files(...)``: Polling for completed video/photo thumbnails
    - ``cleanup_orphaned_uploads(...)``: Polling orphaned upload cleanup
    """

    @staticmethod
    def get_compressed_files():
        """
        Poll S3 for completed compression jobs and update file records.

        ----

        For each pending compression request:

        - Check if the compressed file exists in S3
        - If found, update the File.compressed_file and delete the request
        - If timed out, apply retry logic (see CronUtilities.handle_timeout)

        ----

        Compression location varies by file type:

        - Videos: ``.mp4`` in ``compressed/``
        - Photos: ``.webp`` in ``compressed/``

        ----

        :param:  None

        :return: None
        :rtype: None
        """

        # Retrieve all pending compression requests
        timeout = timezone.now() - timedelta(minutes=AWSPollingUtilities.PROCESSING_TIMEOUT_MINUTES)
        pending = (
            CompressionRequest.objects.filter(
                created_at__gte=timeout,
                file__is_compressed=False,
            )
            .select_related("file")
            .select_for_update()
        )

        # Start compressing waiting requests
        with transaction.atomic():
            for compression_req in pending:
                file = compression_req.file

                s3_compressed_key = AWSStorageUtilities.get_aws_s3_compressed_key(file)
                aws_client = AWSClientFactory.get_s3()
                compression_is_ready = AWSPollingUtilities.s3_object_exists(aws_client, s3_compressed_key)

                if compression_is_ready:
                    FileDeletionUtilities.delete_raw_file(file.source)
                    file.refresh_from_db(fields=["source", "is_compressed"])

                    file.source = s3_compressed_key
                    file.storage_key = s3_compressed_key
                    file.is_compressed = True
                    file.save(update_fields=["is_compressed", "source", "storage_key"])
                    compression_req.delete()

        # Handle timeout for awaiting requests
        AWSPollingUtilities.s3_handle_timeout(timeout)

    @staticmethod
    def get_thumbnail_files():
        """
        Poll S3 for completed thumbnail jobs and update File records.

        ----

        For each pending ThumbnailRequested:

        - Check if the thumbnail file exists in S3
        - If found, update the File.thumbnail and delete the request
        - If timed out, apply retry logic (see CronUtilities.handle_timeout)

        ----

        Thumbnail location varies by file type:

        - Videos: ``.webp`` (frame 0) in ``thumbnails/``
        - Photos: ``.webp`` in ``thumbnails/``

        ----

        :param: None

        :return: None
        """

        # Check for pending thumbnail requests
        timeout = timezone.now() - timedelta(minutes=AWSPollingUtilities.PROCESSING_TIMEOUT_MINUTES)
        pending = (
            ThumbnailRequest.objects.filter(created_at__gte=timeout, file__thumbnail__in=[None, ""])
            .select_related("file")
            .select_for_update()
        )

        aws_client = AWSClientFactory.get_s3()

        # Process each awaiting thumbnail
        with transaction.atomic():
            for thumbnail_req in pending:
                file = thumbnail_req.file
                s3_thumbnail_key = AWSStorageUtilities.get_aws_s3_thumbnail_key(file)
                thumbnail_is_ready = AWSPollingUtilities.s3_object_exists(aws_client, s3_thumbnail_key)

                # Handle creation if the thumbnail was made
                if thumbnail_is_ready:
                    file.refresh_from_db(fields=["thumbnail"])

                    file.thumbnail = s3_thumbnail_key
                    file.save(update_fields=["thumbnail"])
                    thumbnail_req.delete()

        # Handle timeout for awaiting requests
        AWSPollingUtilities.s3_handle_timeout(timeout)

    @staticmethod
    def cleanup_orphaned_uploads():
        """
        Delete unfinished uploads older than 24 hours.

        Removes failed storage request records.
        This prevents accumulation of orphaned uploads.

        ----

        Uploads are considered orphaned if:

        - ``finished_at`` is still ``None``
        - ``created_at`` is older than 24 hours

        ----

        :param: None

        :return: None
        :rtype: None
        """

        timeout = timezone.now() - timedelta(hours=24)
        FileStorageRequest.objects.filter(
            created_at__lt=timeout,
        ).delete()
