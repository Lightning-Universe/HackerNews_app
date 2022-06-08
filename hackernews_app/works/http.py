import logging

import lightning as L
import requests


class HTTPRequest(L.LightningWork):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = None
        self.response = {}

    def get(self, url):
        self.run(action="get", url=url)

    def _get(self, url):
        try:
            response = requests.get(url)
            self.status_code = response.status_code
            self.response = response.json()
        except requests.exceptions.MissingSchema as e:
            logging.error(e)

    def run(self, action, *args, **kwargs):
        if action == "get":
            self._get(*args, **kwargs)
