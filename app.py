import lightning as L
from hackernews_app.flows import HackerNewsLiveStories
from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS

class HackerNewsApp(L.LightningFlow):

    def __init__(self):
        super().__init__()
        self.hacker_news_live_stories = HackerNewsLiveStories(
            project_id=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id,
            topic="hacker-news-items"
        )

    def run(self):
        self.hacker_news_live_stories.run()

if __name__ == "__main__":
    app = L.LightningApp(HackerNewsApp())
