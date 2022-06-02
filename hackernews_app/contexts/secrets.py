"""
TODO: Replace with a proper secrets management.
"""
from google.oauth2 import service_account


def get_secrets():
    return {
        "type": "service_account",
        "project_id": "eric-lightning-app",
        "private_key_id": "ddd711ee9ad14fc6c8b0d5f3036b77eb9e5bd1a4",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDn6vXgC0DePXfm\nC1mewXu0M6l2OMtrnv0QsqJlw3DasojDQhFEFYLqjDd+MucMzPgiVXXsdZq866E4\n+vro6kVPkThhQCvVK3sG1JNPMreRT9NvSyMYyRqOAeyV8Rbi8EyKpr6+DzaEJn+T\nFkWwuPptPXsRsJL839Vsw2zS4PBqzo7VCOpu0+pvvi+hL+PbqzHOfnPwagpb/9yo\npMU441aS46HyHJVRn/cXHxQbOo333I6SoRxBNaMmD1zczK8Fx6xb3+46MU9OGBX7\nWiSOY2477/82vniBVN0QvQlR7fyT2e8PkwI8S2dlho9gdhnpebqHsW2zZ9GHnWW3\nwXpOBZNNAgMBAAECggEANcH7vPN21Z0TeA5M95T7XvWztAztsDRiDjcOGD8hn3wP\nYg1kMa830bTvXxAfCRNQ+Cpto4JOPDj1Pd9FfmxhZRRxKG/GyUqjIZ3wSIUl0mfZ\nx5w31jS1dFHjXI1OJAwV/fSxVZ5yoVbILxjUTibOm7hK2PqgU7/xuZyiEs6jw+nM\n5+JziU810uj99USg5ugA1t1ucwJxTsP9939/MMuGPYSPAHz77yTtTn26lZa6ofBv\nfY00y5wXivk/jO3ZUS1j4a2pX6SXrGBCUvufm7whuqimy98iPHS/N7sQ4bvwATGp\ng2JJr3QIRTzTlJ7BcZyO3TvjCuimKUvwGpibwtfaMQKBgQD594cLrXEOQuNzviYi\nWvwZz9njEAQWfqcGJBqlMAO/L9PsH5KlxdPA2Rf91yQ7/IEeZRITcdaJ+RlVSV4r\naFNJlUdSjZmEi1h63beUypDkAqXgcxdx2AHluZeFZgWlhQTUazyQL/UDR2YA/JV8\njyhvX2HXUN2kYdtfNudWTq/NfQKBgQDtg+myCOWZLLOfhEVApQ5T29bb6ywu+AXI\nvMH+fqFU7l/aVuj0uL1WNzxd7Vh9RXUnvZ4G1C8/0NK3Wqa3B4u/+CTX/59S3FSk\n5fuYuEdzL8qVDh0DGqtsLstZC6Nrq3Effpa5vXnME3328aEOlzuK4tXIOkK9iODp\nh8DpYigGEQKBgBxwLM0HTnVw5q+kUnJWJ5hILWHH0K8+eYIZWW6xp7t4lYOnk+eI\nOi8Wg8Q9VcH9WDM9DHFp4h6QWHF7h1so41DbyuF5ep25vLc9wkULRrCqHHUMov4w\ntQaNts9WbA4ItCP2j01YJ2fYF6LFGbyyDMee8mKssIqjF3IdrPQEv7uBAoGBAKLQ\ng1lMqf8nWnZl2Ico3jpz/8Q/YMlNscFaS21mZrdutHxaiVSAcyHvuUz1z2wIOfgl\nDnfF6iHHxzpzRMdAv/a3ZqI+k3vcl5V2JdMZt7jpMOiehRrEpHADX9fJl5vOKTya\nrT3j+eMAFaA7INl8qA9b0YpxDaEZfHv5WC9j3uXRAoGBAIofIJnrFDU2upyBHPv1\nP5v9SuaOGJFGG+N/ld2YcuW6U8zqXMbW2gzvBj5eaZCU4kXsEF6CURHNPKdxRn6N\nQFBIALMC9L55tDiXs2lwK9Gq176g97xUbzdPVKx2IhBA5naC2HPpwZnuJKqWE3Lm\nLk7HPVl78yetDLxGH6gNEegF\n-----END PRIVATE KEY-----\n",
        "client_email": "lightningapp-hackernews@eric-lightning-app.iam.gserviceaccount.com",
        "client_id": "112101504526717519348",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lightningapp-hackernews%40eric-lightning-app.iam.gserviceaccount.com",
    }


__SECRETS = get_secrets()

LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS = service_account.Credentials.from_service_account_info(__SECRETS)
