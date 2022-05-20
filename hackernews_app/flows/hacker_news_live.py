import time
import logging
import lightning as L
from hackernews_app.works.hacker_news import HackerNewsGetItem, HackerNewsSubscriber

class HackerNewsLiveStories(L.LightningFlow):
    """ This flow runs endlessly

    """

    def __init__(
        self,
        project_id: str,
        topic: str,
        time_interval: int = 5,
    ):
        super().__init__()
        self.time_interval = time_interval
        self.item_getter = HackerNewsGetItem(project_id, topic, run_once=False)
        self.subscriber = HackerNewsSubscriber(
            project_id=project_id,
            topic_name=self.item_getter.topic_name,
            subscription="hacker-news-items-subscription",
            run_once=False
        )

    def run(self):

        # Query the item api for the newest story.
        # If there there is an item then pass it to the stream.

        if self.item_getter.data:
            self.subscriber.run()
        # The property of the work isn't changing
        else:
            self.item_getter.run()
        print(f"getter data: {self.item_getter.data}")

        print(f"subscriber: {self.subscriber.messages}")
        if self.item_getter.has_started:
            return

        time.sleep(self.time_interval)


