#!/usr/bin/env python

import os
import sys

# ---------------------- #
# Application Entrypoint #
# ---------------------- #


def main():
    """
    Run administrative tasks for the backend
    application.

    ----

    :param: None

    :return: None
    :rtype: None
    """

    # Get the set the default settings module
    # to be the development kit.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

    # Import shell script for management
    # handling
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Execute given command-line arguments
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
