from django.conf import settings

from files.api.aws.views import RegisterAWSStorageAPIView, RequestAWSStorageAPIView
from files.api.local.views import RegisterLocalStorageAPIView, RequestLocalStorageAPIView, UploadToLocalStorageAPIView

# ---------------------- #
# Main File-Upload Setup #
# ---------------------- #

# If any storage providers are changed or added,
# simply add the required views for handling the
# required upload scheme here.
#
# They should follow mainly the same format of:
#
# 1. Request storage from the cloud
# 2. Store directly to cloud (or local)
# 3. Register the storage in the backend

if settings.FILE_UPLOAD_STORAGE == "LOCAL":
    RequestStorageAPIView = RequestLocalStorageAPIView
    RegisterStorageAPIView = RegisterLocalStorageAPIView
    UploadToStorageAPIView = UploadToLocalStorageAPIView

elif settings.FILE_UPLOAD_STORAGE == "S3":
    RequestStorageAPIView = RequestAWSStorageAPIView
    RegisterStorageAPIView = RegisterAWSStorageAPIView
    UploadToStorageAPIView = None
