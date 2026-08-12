from django.conf import settings
from django.core.exceptions import ValidationError

# -------------------- #
# MIME type validation #
# -------------------- #


class FileValidationUtilities:
    """
    Utility class for providing file field
    validation.

    ----

    **Provides** the functionality:

    -- ``validate_mime_type(...)``: Checks if the given MIME type is valid
    """

    @staticmethod
    def validate_mime_type(mime_type):
        """
        Validate that the MIME type is in our allowed list.
        Throws an exception if it isn't.

        ----

        :param mime_type: The given MIME type
        :rtype: str

        :return: None
        :rtype: None
        """

        if mime_type not in settings.ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"Unsupported MIME type '{mime_type}'. Allowed types: {sorted(settings.ALLOWED_MIME_TYPES)}"
            )
