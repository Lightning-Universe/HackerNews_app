import time
import logging
import lightning as L
from hackernews_app.works.hacker_news import HackerNewsGetItem

class HackerNewsLiveStories(L.LightningFlow):
    """ This flow runs endlessly

    """

    def __init__(self, time_interval: int = 5):
        super().__init__()
        self.time_interval = time_interval
        self.item_getter = HackerNewsGetItem(run_once=False)

    def run(self):

        # Query the item api for the newest story.
        # If there there is an item then pass it to the stream.
        # If there is non then do nothing.
        self.item_getter.run()
        if self.item_getter.has_started:
            return
        time.sleep(self.time_interval)
