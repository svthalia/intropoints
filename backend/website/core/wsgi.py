import os

from django.core.wsgi import get_wsgi_application

# -------------- #
# Internal Proxy #
# -------------- #


# By default, the proxy reverts to development settings,
# this is overridden when deploying via a run of the ``wsgi``
# executable.

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
application = get_wsgi_application()
