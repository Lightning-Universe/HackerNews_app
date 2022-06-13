import datetime as dt
import json
import logging
import pickle
import time

import lightning as L
from lightning_bigquery import BigQuery

from hackernews_app.api.hackernews import constants
from hackernews_app.contexts.secrets import get_secrets
from hackernews_app.works.hacker_news import HackerNewsGetItem, HackerNewsRequestAPI, HackerNewsSubscriber
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
        self.item_getter = HackerNewsGetItem(secrets["project_id"], topic, run_once=False)
        self.subscriber = HackerNewsSubscriber(
            project_id=secrets["project_id"],
            topic_name=self.item_getter.topic_name,
            subscription="hacker-news-items-subscription",
            run_once=False,
        )
        self.bq_inserter = BigQuery(project=secrets["project_id"], location="US", credentials=secrets)
        self.is_bq_inserting = False

        self.topic_classifier = TopicClassification(None)
        self.story_encoder = StoryEncoder(None)

        self.hn_data = None
        self.topics = None
        self.story_encodings = None

    def run(self):
        if self.hn_data is None:
            if self.item_getter.has_succeeded and self.item_getter.data and self.is_bq_inserting is False:
                self.is_bq_inserting = True

                self.hn_data = [
                    {**json.loads(data), **{"created_at": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}}
                    for data in self.item_getter.data
                ]
        else:
            stories = [row for row in self.hn_data if row["type"] == "story" and row["title"] is not None]
            stories = [{"title": row["title"], "id": row["id"]} for row in stories]

            stories = [{"title": "The Tech blog published a new article", "id": str(i + 1000)} for i in range(5)]

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

            # TODO: Comeback to enabule the subscriber. There is an issue with passing/receiving data from pubsub.
            #       It is encoding the byte representation as a literal string. i.e. 'foo bar' gets received by
            #       the subscriber as byte("b'foo bar'") -- creating issues with urls.
            # self.subscriber.run()

        if self.bq_inserter.has_succeeded and self.is_bq_inserting is True:
            self.is_bq_inserting = False
            logging.info("Resetting item getter data")
            self.item_getter.data = []

        if not self.item_getter.has_started:
            self.item_getter.run()

        if len(self.subscriber.messages) > 0:
            logging.info(f"subscriber: {self.subscriber.messages}")
            self.on_after_run()

        time.sleep(self.time_interval)

    def on_after_run(self):
        self.subscriber.messages = []


class LastGroupLoader(L.LightningWork):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.last_group = None

    def run(self, filepath: str):
        with open(filepath, "rb") as fp:
            last_group = pickle.load(fp)

        self.last_group = int(last_group.maxvalue.iloc[0]) + 1 if len(last_group) else 1


class HackerNewsHourly(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.should_execute = True  # TODO: change this to False

        # Run one time to get the data we need.
        secrets = get_secrets()
        self.last_group_getter = BigQuery(project=secrets["project_id"], location="US", credentials=secrets)
        self.last_group_loader = LastGroupLoader(run_once=True)

        # Recurring runs
        self.api_client = HackerNewsRequestAPI()
        self.inserter = BigQuery(project=secrets["project_id"], location="US", credentials=secrets)
        self.to_insert = True

    def run(self):

        if self.last_group_loader.last_group is None:

            query = """
                select coalesce(max(group_id), 1) maxvalue
                from `hacker_news.top_stories`
            """

            self.last_group_getter.run(
                sqlquery=query,
                to_dataframe=True,
            )

        if self.last_group_getter.has_succeeded:
            self.last_group_loader.run(self.last_group_getter.result_path)

        # Start recurring loop.

        if self.schedule("*/5 * * * *"):
            self.should_execute = True

        if self.should_execute is False:
            return

        # Get data
        self.api_client.run(constants.HACKERNEWS_TOP_STORIES_ENDPOINT)

        if self.api_client.response_data and self.last_group_loader.last_group is not None and self.to_insert:

            self.to_insert = False

            self.inserter.run(
                sqlquery=f"""
                INSERT INTO `hacker_news.top_stories` (story_id, created_at, group_id)
                VALUES {
                    ",".join([
                        str(val)
                        for val in tuple(
                            (
                                str(story_id),
                                dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                                self.last_group_loader.last_group
                            )
                            for story_id in self.api_client.response_data
                        )
                    ])}
                """,
            )

        if self.inserter.has_succeeded and self.api_client.has_succeeded:
            self.on_after_run()

    def on_after_run(self):
        self.should_execute = False
        self.to_insert = True
        self.last_group_loader.last_group += 1
