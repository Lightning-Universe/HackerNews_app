"""
TODO: Replace with a proper secrets management.
"""
import json
import logging
import os
from pathlib import Path

from google.oauth2 import service_account


def get_secrets():
    filepaths = [
        os.path.join(os.path.dirname(__file__), ".secrets.json"),
    ]

    for filepath in filepaths:
        if Path(filepath).is_file():
            logging.info(f"Using secrets from {filepath}")
            return json.load(open(filepath))

    logging.error(f"Did not find secrets in {filepaths}")


__SECRETS = get_secrets()
LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS = (
    service_account.Credentials.from_service_account_info(__SECRETS)
)