# Copyright (C) 2009 Robert Collins <robertc@robertcollins.net>
# Licenced under the txaws licence available at /LICENSE in the txaws source.

"""Credentials for accessing AWS services."""

from ConfigParser import SafeConfigParser
import os

from txaws.exception import CredentialsNotFoundError
from txaws.util import hmac_sha256, hmac_sha1


__all__ = ["AWSCredentials"]


ENV_ACCESS_KEY = "AWS_ACCESS_KEY_ID"
ENV_SECRET_KEY = "AWS_SECRET_ACCESS_KEY"
ENV_SHARED_CREDENTIALS_FILE = "AWS_SHARED_CREDENTIALS_FILE"


class _CompatCredentialsNotFoundError(CredentialsNotFoundError, ValueError):
    """
    To nudge external code from ValueErrors, we raise a compatibility subclass.

    """


class AWSCredentials(object):
    """Create an AWSCredentials object.

    @param access_key: The access key to use. If None the environment variable
        AWS_ACCESS_KEY_ID is consulted.
    @param secret_key: The secret key to use. If None the environment variable
        AWS_SECRET_ACCESS_KEY is consulted.
    """

    def __init__(self, access_key="", secret_key=""):
        if not access_key:
            access_key = os.environ.get(ENV_ACCESS_KEY)
            if not access_key:
                access_key = _load_shared_credentials().get(
                    "default", "aws_access_key_id",
                )
        if not secret_key:
            secret_key = os.environ.get(ENV_SECRET_KEY)
            if not secret_key:
                secret_key = _load_shared_credentials().get(
                    "default", "aws_secret_access_key",
                )

        self.access_key = access_key
        self.secret_key = secret_key

    def sign(self, bytes, hash_type="sha256"):
        """Sign some bytes."""
        if hash_type == "sha256":
            return hmac_sha256(self.secret_key, bytes)
        elif hash_type == "sha1":
            return hmac_sha1(self.secret_key, bytes)
        else:
            raise RuntimeError("Unsupported hash type: '%s'" % hash_type)


def _load_shared_credentials():
    credentials_path = os.environ.get(
        ENV_SHARED_CREDENTIALS_FILE,
        os.path.expanduser("~/.aws/credentials"),
    )
    config = SafeConfigParser()
    if not config.read([credentials_path]):
        raise _CompatCredentialsNotFoundError(
            "Could not find credentials in the environment or filesystem",
        )
    return config
