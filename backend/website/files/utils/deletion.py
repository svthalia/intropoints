from pathlib import Path

from django.conf import settings

# ----------------------- #
# File deletion utilities #
# ----------------------- #


class FileDeletionUtilities:
    """
    Utility class to handles base file deletion.
    Should incorporate any base methods for deleting
    file data and metadata.

    ----

    **Provides** the functionality:

    - ``delete_raw_file(...)``: Deletes the given physical raw file
    """

    @staticmethod
    def delete_raw_file(raw_file):
        """
        Deletes the raw file from the physical
        storage manager.

        ----

        :param raw_file: The raw file to delete
        :type raw_file: django.core.files.File

        :return: None
        :rtype: None
        """

        if settings.FILE_UPLOAD_STORAGE == settings.LOCAL_STORAGE:
            FileDeletionUtilities._delete_raw_local_file(raw_file)
        else:
            FileDeletionUtilities._delete_raw_aws_file(raw_file)

    # ---------------------- #
    # Internal Functionality #
    # ---------------------- #

    @staticmethod
    def _delete_raw_local_file(raw_file):
        """
        Deletes the raw file from the local manager,
        including any empty folders it leaves behind.

        ----

        :param raw_file: The raw file to delete
        :type raw_file: django.core.files.File

        :return: None
        :rtype: None
        """

        file_path = Path(settings.MEDIA_ROOT) / raw_file.name
        current_dir = file_path.parent
        media_root = Path(settings.MEDIA_ROOT).resolve()

        raw_file.delete()

        while (
            current_dir.is_dir()
            and current_dir.exists()
            and current_dir.resolve() != media_root
            and not any(current_dir.iterdir())
        ):
            empty_dir = current_dir
            current_dir = current_dir.parent
            empty_dir.rmdir()

    @staticmethod
    def _delete_raw_aws_file(raw_file):
        """
        Deletes the raw file from the aws s3
        storage manager.

        ----

        :param raw_file: The raw file to delete
        :type raw_file: django.core.files.File

        :return: None
        :rtype: None
        """

        raw_file.delete()
