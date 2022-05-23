import logging
import os
import time

import requests

from hackernews_app.api import constants


def request_wrap(func):
    def wrapper_request(*args, **kwargs):
        retries = kwargs.get("retries", 3)
        for _ in range(retries + 1):
            try:
                response = func(*args, **kwargs)

                # Wait 1 minute if we've been rate limited.
                if response.status_code == 429:
                    logging.warning("Sleeping for 1 minute before getting rate limited")
                    time.sleep(60)
                if response.status_code != 200:
                    logging.info(
                        f"HTTP status code {response.status_code} observed. Message received is {response.content}"
                    )
                logging.info(f"Successfully transmitted data: {response.url}")
                return response
            except Exception as error:
                logging.error(f"Failed to pass {args, kwargs}", f"Error: {error}")

        logging.error(f"Failed to transmit payload after {retries} retries.")

    return wrapper_request


class RESTAPI:
    def __init__(
        self,
        api_key: str = "",
        params: Optional[Dict] = None,
        base_url: str = constants.HACKERNEWS_BASEURL,
    ):

        self.api_key = api_key
        self.client = requests
        self.params = params
        self.base_url = base_url
        self.url = None

    @request_wrap
    def get(self, path: str, params: dict = None) -> requests.Response:

        self.url = "/".join([self.base_url, path])
        logging.info(self.url)
        return self.client.get(
            url=self.url,
            params=params or self.params,
        )