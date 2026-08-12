import os
from pathlib import Path

# ---------------- #
# General settings #
# ---------------- #

# Most of these settings are related to
# server location and language.

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = "core.urls"

LANGUAGE_CODE = "en-us"
USE_TZ = True
TIME_ZONE = 'Europe/Amsterdam'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------- #
# Custom settings #
# --------------- #


# Any other suitable additional settings that
# are used within the app.

SUBMISSION_LOCK_TIMEOUT = 15

# ---------------- #
# Sub applications #
# ---------------- #


# All the sub applications that the
# current project relies upon.
#
# This includes django / API modules,
# and any other external dependencies.

INSTALLED_APPS = [
    # Core applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "import_export",

    # API dependency & styling
    "rest_framework",
    "drf_spectacular",

    # Filters
    "rangefilter",
    "autocompletefilter",
    "django_filters",

    # OAuth services
    "oauth2_provider",

    # Cors policy
    "corsheaders",

    # Custom apps
    "core",
    "users",
    "stores",
    "challenges",
    "files",
    "submissions",
    "accounts",
    "teams",
    "tournaments",
    "login",
]


# ----------------------- #
# Middleware applications #
# ----------------------- #


# The middleware used in order to fulfill
# certain roles within the application.
#
# This includes protocol settings, or login
# functionality...

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ------------ #
# Login Config #
# ------------ #


# The current login configuration for the
# application.
#
# Sets the basic user mode and the base login
# URL endpoint.

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/login/thalia/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# -------------- #
# HTML Templates #
# -------------- #


# The templates used within the whole
# backend application.
#
# Currently, these are only necessary when
# overriding backend functionality, since
# the frontend is handled by an entirely different
# framework.

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["core/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# --------------------- #
# Internal Proxy Config #
# --------------------- #


# Defines the internal proxy that Django
# uses in order to route between applications.
#
# Currently, we rely on the basic WSGI.

WSGI_APPLICATION = "core.wsgi.application"

# --------------------- #
# Authentication Config #
# --------------------- #


# The authentication settings that define password
# and user validation.
#
# They also provide authentication endpoints for 3rd
# party authentication, its scopes and protocol access.
#
# The password validators are only needed for the Admin user,
# since any other user relies on 3rd party authentication.

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

OAUTH_API_AUTHORIZATION_ENDPOINT = "oauth/authorize/"
OAUTH_API_REDIRECT_ENDPOINT = "auth/callback/"

OAUTH2_PROVIDER = {
    "ALLOWED_REDIRECT_URI_SCHEMES": ["http", "https"],
    "SCOPES": {
        "read": "Authenticated read access to the backend",
        "write": "Authenticated write access to the backend",
    },
}

# ------------ #
# API Settings #
# ------------ #

# Settings that configure API authentication,
# schema versioning and pagination.

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
}

# Specifies the required settings for displaying the
# interactive API documentation page.
#
# Customizes most of it such that it has the Thalia
# look.
SPECTACULAR_SETTINGS = {
    "TITLE": "Backend API",
    'DESCRIPTION': 'API for the Scavenger Hunt Website',

    # For now the only use for the API is within the website's own
    # components, so we don't need versioning
    'VERSION': '1.0.0',

    # Custom prefix, since I like my namespaces
    'SCHEMA_PATH_PREFIX': r'/api/',

    # Never show the schema endpoint
    "SERVE_INCLUDE_SCHEMA": False,

    # Slight customization
    "REDOC_UI_SETTINGS": {
        # Remove downloadable schema
        "hideDownloadButton": True,

        # Custom Theme settings
        "theme": {
            # Base color settings
            "colors": {
                # Http tag color settings
                "http": {
                    "get": "#e62272",
                    "post": "#e62272",
                    "put": "#e62272",
                    "delete": "#e62272",
                    "patch": "#e62272",
                },

                # Base response settings
                "responses": {
                    # Success code color - everything that includes
                    # 2xx OK codes.
                    #
                    # Magenta background with white text
                    "success": {
                        "backgroundColor": "#e62272",
                        "color": "#ffffff",
                    },

                    # Error code color - everything that includes
                    # 4xx OK codes.
                    #
                    # Black Background with white text
                    "error": {
                        "backgroundColor": "#000000",
                        "color": "#ffffff",
                    }
                },
            },

            # Right-side response panel
            #
            # Dark Magenta background with white text
            "rightPanel": {
                "backgroundColor": "#36091b",
                "textColor": "#ffffff",
            },

            # Left-side sidebar that indicates where in the
            # api documentation you are located
            "sidebar": {
                "backgroundColor": "#ffffff",
                "textColor": "#333333",
                "activeBackgroundColor": "#d4d4d4",
                "activeTextColor": "#f06ea3",
                #
                "level1Items": {
                    "activeBackgroundColor": "#d4d4d4"
                }
            }
        },
    },
}

# ----------- #
# CORS policy #
# ----------- #


# The Cross-Origin Resource Sharing scheme, that
# currently accepts only external resources provided
# by the 3rd party authentication handler.

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/(?:oauth)/.*"

# ------------------ #
# Allowed File Types #
# ------------------ #

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/heic",
    "image/heif",
    "video/mp4",
    "video/webm",
    "video/quicktime",
}

# ----------- #
# AWS Storage #
# ----------- #


# These fields need to be here in order to
# allow django to properly compile regardless
# of setting choices.

AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_S3_REGION_NAME = None
AWS_STORAGE_BUCKET_NAME = None
AWS_DEFAULT_ACL = None
AWS_PRESIGNED_EXPIRY = 0
FILE_MAX_SIZE = 0

# --------------- #
# AWS Compression #
# --------------- #

AWS_MEDIACONVERT_TEMPLATE_NAME = None
AWS_MEDIACONVERT_ENDPOINT_URL = None
AWS_MEDIACONVERT_ROLE_ARN = None
AWS_PHOTO_COMPRESSION_ROLE_ARN = None
AWS_IMAGE_COMPRESSION_FUNCTION_NAME = None

# ------------ #
# File Storage #
# ------------ #

# Storage types for file retrieval

LOCAL_STORAGE = "LOCAL"
S3_STORAGE = "S3"

# Determines where the application
# stores its files internally

FILE_UPLOAD_STORAGE = LOCAL_STORAGE

# ----------------- #
# File base folders #
# ----------------- #

# The basic folders that are used for compression
# or thumbnails

FILE_STORAGE_COMPRESSION_FOLDER = "compressed"
FILE_STORAGE_THUMBNAIL_FOLDER = "thumbnails"

# Files for application specific storages

FILE_STORAGE_BASE_FOLDER = "files"
FILE_STORAGE_SUBMISSIONS_FOLDER = "submissions"
FILE_STORAGE_CHALLENGES_FOLDER = "challenges"

ALLOWED_FILE_STORAGE_FOLDERS = [
    FILE_STORAGE_BASE_FOLDER,
    FILE_STORAGE_SUBMISSIONS_FOLDER,
    FILE_STORAGE_CHALLENGES_FOLDER
]
