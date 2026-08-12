from django.urls import path

from files.api import RegisterStorageAPIView, RequestStorageAPIView, UploadToStorageAPIView

app_name = "files_api"

# These url patterns allow for a seamless
# integration and switch between storage options.
#
# Sort-of acts like an interface, with the API endpoints:
#
#  - ``RequestStorage``
#  - ``UploadToStorage`` (If necessary)
#  - ``RegisterStorage``
#
#
#
# ``/api/files/request-storage/``
#   -> Make a file storage request
#
# ``/api/dile/upload-to-storage/``
#   -> Upload the given file to the selected storage
#
# ``/api/files/register-storage/``
#   -> Register the completed storage request

urlpatterns = [
    path("request-storage/", RequestStorageAPIView.as_view()),
    path("register-storage/", RegisterStorageAPIView.as_view()),
]

# Check if the current storage option allows for
# uploading files, otherwise do not include the URL
if UploadToStorageAPIView:
    urlpatterns += [path("upload-to-storage/", UploadToStorageAPIView.as_view())]
