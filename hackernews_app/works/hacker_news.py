import json
import logging
import urllib
from typing import Any

import lightning as L
import requests

from hackernews_app.api import RESTAPI
from hackernews_app.api.hackernews import constants

STORIES_SCHEMA = [
    "title",
    "url",
    "text",
    "dead",
    "by",
    "score",
    "time",
    "timestamp",
    "type",
    "id",
    "parent",
    "descendants",
    "ranking",
    "deleted",
    "created_at",
]


class HackerNewsGetItem(L.LightningWork):
    """Gets new stories.

    Args:
        max_item_id: the last story to start loading from.
    """

    def __init__(self, project_id: str, topic: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = constants.HACKERNEWS_BASEURL
        self.data = []
        self.max_item_id = None
        self.project_id = project_id
        self.topic = topic
        self.topic_name = f"projects/{project_id}/topics/{topic}"
        self.publish_timeout = 60
        self.max_stories = 20
        self.num_stories = 0
        self.fetching = False

    def run(self, _: Any, url: str):
        if self.max_item_id is None:
            response = requests.get(f"{url}/api/max_item_id")
            self.max_item_id = int(response.json()["max_item_id"]) + 1

        client = RESTAPI(self.base_url)

        if self.max_item_id is None:
            response = client.get(constants.HACKERNEWS_MAX_ITEM_ENDPOINT)
            if response.status_code == 200:
                self.max_item_id = response.json()

        while self.num_stories < self.max_stories:
            _data = {col: None for col in STORIES_SCHEMA}

            response = client.get(constants.HACKERNEWS_ITEMS_ENDPOINT.format(id=self.max_item_id))
            data = response.json()

            if response.status_code != 200 or data is None:
                logging.info(f"Did not see anything. The last item retrieved: {self.max_item_id}")
                # TODO: revisit when there is time to look into using the Payload API for serializing bytes
                #       The current implementation can publish the text but there is some decoding issues from
                #       the subscriber.
                # self.publish()
                return

            if data.get("url"):
                data["url"] = urllib.parse.quote(data["url"])

            _data.update(data)
            _data = {k: _data[k] for k in STORIES_SCHEMA}
            self.data = [*self.data, json.dumps(_data)]
            # logging.info(f"Found a new item: {data}")
            logging.info(f"The last item retrieved: {self.max_item_id}")
            self.max_item_id += 1
            self.num_stories += 1

        self.num_stories = 0
