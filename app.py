import lightning as L
from hackernews_app.flows import HackerNewsLiveStories
import logging
class HackerNewsApp(L.LightningFlow):

    def __init__(self):
        super().__init__()
        self.hacker_news_live_stories = HackerNewsLiveStories()

    def run(self):
        self.hacker_news_live_stories.run()

if __name__ == "__main__":
    app = L.LightningApp(HackerNewsApp())
