import logging
import requests
import lightning as L

from hackernews_app.api import RESTAPI, constants
from hackernews_app.api.hackernews import HackerNewsAPI, constants


class HackerNewsGetItem(L.LightningWork):
    """Gets new stories.

    Args:
        max_item_id: the last story to start loading from.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = constants.HACKERNEWS_BASEURL
        self.data = {}
        self.max_item = None

    def run(self):

        client = RESTAPI(self.base_url)
        if self.max_item is None:
            response = client.get(constants.HACKERNEWS_MAX_ITEM_ENDPOINT)
            if response.status_code == 200:
                self.max_item = response.json()
            else:
                return
        logging.info(self)
        while True:
            logging.info(self)
            response = client.get(constants.HACKERNEWS_ITEMS_ENDPOINT.format(id=self.max_item))
            data = response.json()

            if response.status_code != 200 or data is None:
                print(self.max_item)
                return
            logging.info(data)
            self.max_item += 1
            logging.info(f"The last item retrieved: {self.max_item}")