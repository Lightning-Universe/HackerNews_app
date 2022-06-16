import datetime as dt
import json
import logging
import time

import lightning as L
from lightning_bigquery import BigQuery

from hackernews_app.contexts.secrets import get_secrets
from hackernews_app.works.hacker_news import HackerNewsGetItem
from hackernews_app.works.story_encoder import StoryEncoder
from hackernews_app.works.topic_classification import TopicClassification

logging.basicConfig(level=logging.INFO)


class HackerNewsLiveStories(L.LightningFlow):
    """This flow runs endlessly."""

    def __init__(
        self,
        topic: str,
        time_interval: int = 5,
    ):
        super().__init__()
        secrets = get_secrets()
        self.time_interval = time_interval
        self.item_getter = HackerNewsGetItem(secrets["project_id"], topic, cache_calls=True)
        self.bq_inserter = BigQuery(project=secrets["project_id"], location="US", credentials=secrets)

        self.topic_classifier = TopicClassification(None)
        self.story_encoder = StoryEncoder(None)

        self.hn_data = None
        self.last_fetched_time = -10000000

    def run(self):
        if time.time() - self.last_fetched_time < self.time_interval:
            return

        if self.hn_data is None:
            self.item_getter.run(self.last_fetched_time)

            self.hn_data = [
                {**json.loads(data), **{"created_at": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}}
                for data in self.item_getter.data
            ]
        else:
            stories = [row for row in self.hn_data if row["type"] == "story" and row["title"] is not None]
            stories = [{"title": row["title"], "id": str(row["id"])} for row in stories]

            if stories:
                self.topic_classifier.run(stories)
                self.story_encoder.run(stories)

                self.bq_inserter.insert(
                    json_rows=self.topic_classifier.topics,
                    table="hacker_news.story_topics",
                )

                self.bq_inserter.insert(
                    json_rows=self.story_encoder.encodings,
                    table="hacker_news.story_embeddings",
                )

            self.bq_inserter.insert(
                json_rows=self.hn_data,
                table="hacker_news.items",
            )

            self.hn_data = None
            self.last_fetched_time = time.time()
            logging.info("Resetting item getter data")
            self.item_getter.data = []
