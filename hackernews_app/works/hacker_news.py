from typing import List
import logging
import pickle
import time
import json
import lightning as L
from typing import Callable
import google
from google.cloud import pubsub_v1
from concurrent import futures

from hackernews_app.api import RESTAPI, constants
from hackernews_app.api.hackernews import HackerNewsAPI, constants

from lightning.storage import Path

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

    def run(self):

        client = RESTAPI(self.base_url)

        if self.max_item is None:
            response = client.get(constants.HACKERNEWS_MAX_ITEM_ENDPOINT)
            if response.status_code == 200:
                self.max_item = response.json()

                #TODO: Remove me using this for testing
                self.max_item -= 10

        while True:
            response = client.get(constants.HACKERNEWS_ITEMS_ENDPOINT.format(id=self.max_item))
            data = response.json()

            if response.status_code != 200 or data is None:
                logging.info(f"Did not see anything. The last item retrieved: {self.max_item}")
                self.publish()
                return
            self.data = [*self.data, str(response.content)]
            logging.info(f"Found a new item: {data}")
            self.max_item += 1
            logging.info(f"The last item retrieved: {self.max_item}")


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
                    # Wait 60 seconds for the publish call to succeed.
                    print(publish_future.result(timeout=60))
                except futures.TimeoutError:
                    print(f"Publishing {data} timed out.")

            return callback

        for message in self.data:
            message = str(message)
            future = publisher.publish(self.topic_name, message.encode("utf-8"))
            future.add_done_callback(get_callback(future, message))
            publish_futures.append(future)
        self.data = []
        futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)



class HackerNewsSubscriber(L.LightningWork):

    def __init__(self, project_id, topic_name, subscription="hacker-news-items-subscription", *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.project_id = project_id
        self.topic_name = topic_name
        self.subscription = subscription
        self.subscription_name = f"projects/{project_id}/subscriptions/{subscription}"
        self.messages = []


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
                    "max_messages": 5,
                }
            )

            for msg in response.received_messages:
                print("Received message:", msg.message.data)
                self.messages = [*self.messages, str(msg.message.data)]

            ack_ids = [msg.ack_id for msg in response.received_messages]
            subscriber.acknowledge(
                request={
                    "subscription": subscription_path,
                    "ack_ids": ack_ids,
                }
            )