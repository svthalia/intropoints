import os
from pathlib import Path

from core.settings.base import *
from core.settings.base import BASE_DIR, OAUTH2_PROVIDER

# --------------------------- #
# Django development settings #
# --------------------------- #


# Settings that set up the base variables for
# hosting the backend server locally

DEBUG = True
ALLOWED_HOSTS = []
HOST_BASE_URI = "http://localhost:8000/"
SECRET_KEY = "django-insecure-7%)v)fufju7hgt5zgjv%psfr*dlb7!^xc2vkz$4lrlnq0eu!05"


# ------------ #
# Static pages #
# ------------ #


# Handles the storage of static pages, such as
# the admin styles and actions...

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"


# ------------- #
# Media storage #
# ------------- #


# Handles the storage of local media files
# within the application.

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# --------------------------- #
# Thalia Api & Authentication #
# --------------------------- #


# Settings that configure the endpoints for
# Thalia authentication adn user retrieval.
#
# Most of the settings here are placeholders,
# such that django can still pull and recognize them.

THALIA_API_BASE_URI = "http://localhost:8001"
THALIA_API_AUTHORIZATION_ENDPOINT = "/user/oauth/authorize/"
THALIA_API_ACCESS_TOKEN_ENDPOINT = "/user/oauth/token/"
THALIA_API_OAUTH_CLIENT_ID = os.environ.get("THALIA_API_OAUTH_CLIENT_ID")
THALIA_API_OAUTH_CLIENT_SECRET = os.environ.get("THALIA_API_OAUTH_CLIENT_SECRET")
THALIA_API_OAUTH_REDIRECT_URI = "http://localhost:8000/login/thalia/callback"
THALIA_API_MEMBERS_URL = "/api/v2/members/me"


# ----------------------- #
# Database choice and env #
# ----------------------- #


# The base development database is sqlite
# since it operates on a singular file.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(BASE_DIR) / "db.sqlite3",
    }
}


# --------- #
# OAuth env #
# --------- #


# Overrides some of the basic OAuth settings
# to allow more development flexibility.

OAUTH2_PROVIDER["ALLOWED_REDIRECT_URI_SCHEMES"] = ["http", "https"]
OAUTHLIB_INSECURE_TRANSPORT = "1"


# -------------- #
# Cookie storage #
# -------------- #


# Makes it so that cookies can be accesses in
# development. Never use this otherwise!

SECURE_COOKIES=False


# ------------ #
# File Storage #
# ------------ #


# Retrieves the deployment storage options
# and configures the system storage

FILE_UPLOAD_STORAGE = os.environ.get("DJANGO_FILE_UPLOAD_STORAGE", "LOCAL")
