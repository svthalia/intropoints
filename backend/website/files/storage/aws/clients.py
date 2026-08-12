from functools import partial

import boto3
from django.conf import settings

# ----------- #
# AWS Clients #
# ----------- #


class AWSClientFactory:
    """
    AWS service client factory for creating and managing boto3 clients.

    Provides centralized access to AWS services (s3, lambda, mediaconvert)
    with shared credentials and configuration.
    """

    # Smart, really smart. This genuinely acts like an
    # abstract class without introducing inheritance.
    _create_boto_client = partial(
        boto3.client,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    @classmethod
    def get_s3(cls):
        """
        Get a cached AWS S3 client.

        ----

        :param: None

        :return: The s3 base client
        :rtype: BaseClient
        """

        return cls._create_boto_client(service_name="s3")

    @classmethod
    def get_lambda(cls):
        """
        Get a cached AWS Lambda client.

        ----

        :param: None

        :return: The s3 lambda client
        :rtype: BaseClient
        """

        return cls._create_boto_client(service_name="lambda")

    @classmethod
    def get_mediaconvert(cls):
        """
        Get a cached AWS MediaConvert client.

        ----

        :param: None

        :return: The AWS MediaConvert client
        :rtype: BaseClient
        """

        return cls._create_boto_client(
            service_name="mediaconvert",
            endpoint_url=settings.AWS_MEDIACONVERT_ENDPOINT_URL,
        )
