import time
import logging
import lightning as L
from hackernews_app.works.hacker_news import HackerNewsGetItem

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

    def run(self):

        # Query the item api for the newest story.
        # If there there is an item then pass it to the stream.
        # If there is non then do nothing.

        # The property of the work isn't changing
        self.item_getter.run()

        if self.item_getter.has_started:
            return
        time.sleep(self.time_interval)


class HackerNewsSubscription(L.LightningFlow):

    def __init__(self, project_id, topic, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.project_id = project_id
        self.topic = topic
        self.topic_name = f"projects/{project_id}/topics/{topic}"

    def run(self):
