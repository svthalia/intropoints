import os

from core.settings.base import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# --------------------- #
# Django Deployment env #
# --------------------- #

#TODO !! Debug should be set to false in production
DEBUG = True
HOST_BASE_URI = os.environ.get("DJANGO_BASE_URI")
ALLOWED_HOSTS = [os.environ.get("DJANGO_ALLOWED_HOST")]
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ----------------------- #
# Database choice and env #
# ----------------------- #

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": int(os.environ.get("POSTGRES_PORT", 5432)),
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    }
}

# -------------- #
# Static storage #
# -------------- #

STATIC_ROOT = Path(BASE_DIR) / "static/"
STATIC_URL = "/static/"

# ------------- #
# Media storage #
# ------------- #

MEDIA_ROOT = Path(BASE_DIR) / "media/"
MEDIA_URL = "/media/"

# -------------- #
# Thalia Api env #
# -------------- #

THALIA_API_BASE_URI = os.environ.get("DJANGO_THALIA_API_BASE_URI")
THALIA_API_AUTHORIZATION_ENDPOINT = os.environ.get("DJANGO_THALIA_API_AUTHORIZATION_ENDPOINT")
THALIA_API_ACCESS_TOKEN_ENDPOINT = os.environ.get("DJANGO_THALIA_API_ACCESS_TOKEN_ENDPOINT")
THALIA_API_OAUTH_CLIENT_ID = os.environ.get("DJANGO_THALIA_API_OAUTH_CLIENT_ID")
THALIA_API_OAUTH_CLIENT_SECRET = os.environ.get("DJANGO_THALIA_API_OAUTH_CLIENT_SECRET")
THALIA_API_OAUTH_REDIRECT_URI = os.environ.get("DJANGO_THALIA_API_OAUTH_REDIRECT_URI")
THALIA_API_MEMBERS_URL = os.environ.get("DJANGO_THALIA_API_MEMBERS_URL")

# -------------- #
# Cookie storage #
# -------------- #


SECURE_COOKIES=(not DEBUG)

# ----------- #
# AWS Storage #
# ----------- #


# AWS storage base settings.
# These should be retrieved during deployment for
# obvious reasons.

# The ACL defaults to None since it's assumed
# that a private storage server is preferred -
# I refuse to set my instance to ``public-read``!

AWS_ACCESS_KEY_ID = os.environ.get("DJANGO_AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("DJANGO_AWS_SECRET_ACCESS_KEY", None)
AWS_S3_REGION_NAME = os.environ.get("DJANGO_AWS_S3_REGION_NAME", "eu-north-1")
AWS_STORAGE_BUCKET_NAME = os.environ.get("DJANGO_AWS_STORAGE_BUCKET_NAME", None)
AWS_DEFAULT_ACL = os.environ.get("DJANGO_AWS_DEFAULT_ACL", "DISABLED")
AWS_PRESIGNED_EXPIRY = 3600
FILE_MAX_SIZE = 536870912

if AWS_DEFAULT_ACL == "DISABLED":
    AWS_DEFAULT_ACL = None

# --------------- #
# AWS Compression #
# --------------- #

AWS_MEDIACONVERT_TEMPLATE_NAME = "Compress video file"
AWS_MEDIACONVERT_ENDPOINT_URL = os.environ.get("DJANGO_AWS_MEDIACONVERT_ENDPOINT_URL", "https://mediaconvert.eu-north-1.amazonaws.com")
AWS_MEDIACONVERT_ROLE_ARN = os.environ.get("DJANGO_AWS_MEDIACONVERT_ROLE_ARN", "arn:aws:iam::149327014958:role/service-role/MediaConvert_Default_Role")
AWS_IMAGE_COMPRESSION_FUNCTION_NAME = "compress_image_file"

# ------------ #
# File Storage #
# ------------ #


# Retrieves the deployment storage options
# and configures the system storage

FILE_UPLOAD_STORAGE = os.environ.get("DJANGO_FILE_UPLOAD_STORAGE", "S3")

if FILE_UPLOAD_STORAGE == "S3":
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "querystring_expire": AWS_PRESIGNED_EXPIRY,
                "default_acl": AWS_DEFAULT_ACL
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
