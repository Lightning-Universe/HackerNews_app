import logging
import json
import urllib
import datetime as dt
import lightning as L
from typing import Callable
import google
from google.cloud import pubsub_v1
from concurrent import futures

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

class HackerNewsRequestAPI(L.LightningWork):


    def __init__(self):
        super().__init__()
        self.base_url = constants.HACKERNEWS_BASEURL
        self.response_data = {}

    def run(self, path: str):
        client = RESTAPI(self.base_url)
        response = client.get(path)
        self.response_data = response.json()


class HackerNewsGetItem(L.LightningWork):
    """Gets new stories.

    Args:
        max_item_id: the last story to start loading from.
    """

    def __init__(self, project_id: str, topic: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = constants.HACKERNEWS_BASEURL
        self.data = []
        self.max_item = None
        self.project_id = project_id
        self.topic = topic
        self.topic_name = f"projects/{project_id}/topics/{topic}"
        self.publish_timeout = 60

    def run(self):

        client = RESTAPI(self.base_url)

        if self.max_item is None:
            response = client.get(constants.HACKERNEWS_MAX_ITEM_ENDPOINT)
            if response.status_code == 200:
                self.max_item = response.json()

        while True:
            _data = {col: None for col in STORIES_SCHEMA}

            response = client.get(constants.HACKERNEWS_ITEMS_ENDPOINT.format(id=self.max_item))
            data = response.json()

            if response.status_code != 200 or data is None:
                logging.info(f"Did not see anything. The last item retrieved: {self.max_item}")
                # TODO: revisit when there is time to look into using the Payload API for serializing bytes
                #       The current implementation can publish the text but there is some decoding issues from
                #       the subscriber.
                #self.publish()
                return

            if data.get("url"):
                data["url"] = urllib.parse.quote(data["url"])
            _data.update(data)
            self.data = [*self.data, json.dumps(_data)]
            logging.info(f"Found a new item: {data}")
            logging.info(f"The last item retrieved: {self.max_item}")
            self.max_item += 1


    def publish(self):

        publisher = pubsub_v1.PublisherClient()
        publish_futures = []
        try:
            publisher.create_topic(name=self.topic_name)
        except google.api_core.exceptions.AlreadyExists as _message:
            logging.info(_message)
        def get_callback(
                publish_future: pubsub_v1.publisher.futures.Future, data: str
        ) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
            def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
                try:
                    # Wait self.publish_timeout seconds for the publish call to succeed.
                    print(publish_future.result(timeout=self.publish_timeout))
                except futures.TimeoutError:
                    print(f"Publishing {data} timed out.")

            return callback


        for message in self.data:

            print(f"Message published: {message}")

            future = publisher.publish(self.topic_name, message)
            future.add_done_callback(get_callback(future, message))
            publish_futures.append(future)

        futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)



class HackerNewsSubscriber(L.LightningWork):

    def __init__(self, project_id, topic_name, subscription="hacker-news-items-subscription", *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.project_id = project_id
        self.topic_name = topic_name
        self.subscription = subscription
        self.subscription_name = f"projects/{project_id}/subscriptions/{subscription}"
        self.messages = []
        self.unacknowledged = 0


    def run(self):
        # print("Running Subscriber")
        # def callback(message):
        #     message.ack()
        #
        # with pubsub_v1.SubscriberClient() as subscriber:
        #     try:
        #         subscriber.create_subscription(
        #             name=self.subscription_name, topic=self.topic_name)
        #     except google.api_core.exceptions.AlreadyExists as _message:
        #         logging.info(_message)
        #     streaming_pull_future = subscriber.subscribe(self.subscription_name, callback=callback)
        #
        #     try:
        #         # When `timeout` is not set, result() will block indefinitely,
        #         # unless an exception is encountered first.
        #         self.messages = streaming_pull_future.result(timeout=60)
        #     except TimeoutError:
        #         streaming_pull_future.cancel()

        #TODO: look into why async subscriber doesn't work
        with pubsub_v1.SubscriberClient() as subscriber:
            subscription_path = subscriber.subscription_path(self.project_id, self.subscription)
            response = subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": 10,
                }
            )
            ack_ids = []
            for msg in response.received_messages:
                print(f"msg.message.data: {msg.message.data}")
                if not msg.message.data:
                    return

                # TODO: Extremely hacky because of the limitations with passing data between works.
                message = msg.message.data.decode("utf-8").lstrip('b\'').rstrip("\\'")

                self.messages = [
                    *self.messages,
                    {**json.loads(message), **{"created_at": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}}
                ]
                ack_ids.append(msg.ack_id)

            if len(ack_ids) < 0:
                return
            subscriber.acknowledge(
                request={
                    "subscription": subscription_path,
                    "ack_ids": ack_ids,
                }
            )
