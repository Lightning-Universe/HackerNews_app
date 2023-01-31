"""
TODO: Replace with a proper secrets management.
"""
import json
import logging
import os

from google.oauth2 import service_account


def get_secrets():

    if os.getenv("LIGHTNING__GCP_CREDENTIALS"):
        try:
            return json.loads(os.getenv("LIGHTNING__GCP_CREDENTIALS"))
        except json.decoder.JSONDecodeError:
            logging.info("Unable to load secrets from environment.")

    logging.info("Using default dataset that is made public.")
    return {
        "type": "service_account",
        "project_id": "eric-lightning-app",
        "private_key_id": "ddd711ee9ad14fc6c8b0d5f3036b77eb9e5bd1a4",
        "private_key": "-----BEGIN PRIVATE KEY-----\n\n-----END PRIVATE KEY-----\n",
        "client_email": "lightningapp-hackernews@eric-lightning-app.iam.gserviceaccount.com",
        "client_id": "112101504526717519348",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lightningapp-hackernews%40eric-lightning-app.iam.gserviceaccount.com",
    }


__SECRETS = get_secrets()

LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS = service_account.Credentials.from_service_account_info(__SECRETS)
