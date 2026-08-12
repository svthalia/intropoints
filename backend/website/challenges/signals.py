from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Challenge

# ----------------- #
# Deletion Handlers #
# ----------------- #


@receiver(post_delete, sender=Challenge)
def delete_thumbnail(sender, instance, **kwargs):
    """
    Signal that triggers when a challenge is deleted
    either via the normal ``.delete()`` call, or via
    a database bulk delete.

    ----

    Tries to delete the thumbnail of a challenge when itself
    is deleted.

    ----

    :param sender: The client that sent the request
    :type sender: Client

    :param instance: The challenge instance
    :type instance: Challenge

    :param kwargs: Dictionary arguments
    :type kwargs: dict

    :return: None
    :rtype: None
    """

    # Check whether the challenge has a thumbnail
    if instance.thumbnail:
        instance.thumbnail.delete()
