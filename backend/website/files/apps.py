import atexit

from django.apps import AppConfig
from django.conf import settings

# --------------- #
# File app config #
# --------------- #


class FilesConfig(AppConfig):
    """
    Main app configuration for files.

    ----

    Starts the file scheduler on app
    initialization.

    This scheduler makes sure that cloud files
    get compressed properly.

    ----

    Any **CUSTOM** initialization goes here.
    Any non-standard django modules need
    to be imported under:

    - ``ready(...)``
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "files"

    def ready(self):
        """
        Start background task scheduler when the app is ready;
        and import proper signals for deletion.

        ----

        :param: None

        :return: None
        :rtype: None
        """

        # Import signals and specific schedulers
        import files.signals  # noqa: F401
        from files.storage.aws.scheduler import start_scheduler as start_aws_scheduler
        from files.storage.aws.scheduler import stop_scheduler as stop_aws_scheduler

        if settings.FILE_UPLOAD_STORAGE == settings.S3_STORAGE:
            start_aws_scheduler()
            atexit.register(stop_aws_scheduler)
