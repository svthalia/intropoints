from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# --------------------- #
# Global File Scheduler #
# --------------------- #


# Inherits Django's base scheduler functionality in order
# to asynchronously make compression request for the stored
# files.
#
# Apparently, this scheduler is created once per worker,
# so it's a bit hard to synchronize it when it comes to
# checking polls

# Global scheduler creation
_scheduler = None


def get_scheduler():
    """
    Get the global background scheduler instance.

    ----

    :param: None

    :return: The scheduler instance
    :rtype: BackgroundScheduler | None
    """
    return _scheduler


# ---------------------- #
# Scheduler Manipulation #
# ---------------------- #


def start_scheduler() -> None:
    """
    Start the background task scheduler.

    ----

    :param: None

    :return: None
    :rtype: None
    """

    # Declare the scheduler as
    # being global
    global _scheduler
    if _scheduler is not None:
        return

    # Initialize the scheduler
    _scheduler = BackgroundScheduler()

    # ------------- #
    # Local Imports #
    # ------------- #

    # Importing here avoids main app circular
    # imports

    from files.storage.aws.polls import PollS3

    # Poll compressed files every minute
    _scheduler.add_job(
        PollS3.get_compressed_files,
        trigger=IntervalTrigger(seconds=5),
        id="poll_compressed_files",
        name="Poll S3 for compressed files",
        replace_existing=True,
    )

    # Poll thumbnail files every minute
    _scheduler.add_job(
        PollS3.get_thumbnail_files,
        trigger=IntervalTrigger(seconds=10),
        id="poll_thumbnail_files",
        name="Poll S3 for thumbnail files",
        replace_existing=True,
    )

    # Cleanup orphaned uploads every hour at minute 0
    _scheduler.add_job(
        PollS3.cleanup_orphaned_uploads,
        trigger=CronTrigger(hour="*", minute="0"),
        id="cleanup_orphaned_uploads",
        name="Cleanup orphaned uploads",
        replace_existing=True,
    )

    _scheduler.start()


def stop_scheduler() -> None:
    """
    Stop the background task scheduler.

    ----

    :param: None

    :return: None
    :rtype: None
    """

    # Retrieve the global scheduler, and
    # quit if not present
    global _scheduler
    if _scheduler is None:
        return

    _scheduler.shutdown()
    _scheduler = None
