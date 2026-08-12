from django.db.models.signals import post_delete
from django.dispatch import receiver

from files.models.base import File
from files.utils.deletion import FileDeletionUtilities

# ----------------- #
# Deletion Handlers #
# ----------------- #


@receiver(post_delete, sender=File)
def delete_source(sender, instance, **kwargs):
    """
    Post signal that ensures the physical file is also
    safety and fully deleted, including any directories
    that it was stored in.

    ----

    Usually, cloud storage providers do not have true folders,
    so there is no need for recursive calls when the storage is not local

    ----

    :param sender: The client that made the request
    :type sender: Client

    :param instance: The file instance
    :type instance: File

    :return: None
    :rtype: None
    """

    if instance.source:
        FileDeletionUtilities.delete_raw_file(instance.source)
    if instance.thumbnail:
        FileDeletionUtilities.delete_raw_file(instance.thumbnail)
