from django.db.models.signals import post_delete
from django.dispatch import receiver

from submissions.models import Submission

# ----------------- #
# Deletion Handlers #
# ----------------- #

# ------------------- #
# Application signals #
# ------------------- #

# These are custom signals that are called
# for certain model / application procedures
# finish or begin


@receiver(post_delete, sender=Submission)
def delete_file(sender, instance, **kwargs):
    """
    Signal that triggers when a submission is deleted
    either via the normal '.delete()' call, or via
    a database bulk delete.

    ----

    Tries to delete the file of a submission when itself
    is deleted.

    ----

    :param sender: The client that sent this POST
    :type sender: Client

    :param instance: The submission instance
    :type instance: Submission

    :param kwargs: Dictionary arguments
    :type kwargs: dict

    :return: None
    :rtype: None
    """

    # Check whether the challenge has a thumbnail
    if instance.file:
        instance.file.delete()
