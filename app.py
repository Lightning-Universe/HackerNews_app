import lightning as L
from hackernews_app.flows import HackerNewsLiveStories, HackerNewsHourly
from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS

class HackerNewsDataProcesses(L.LightningFlow):

    def __init__(self):
        super().__init__()
        self.hacker_news_live_stories = HackerNewsLiveStories(
            project_id=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id,
            topic="hacker-news-items"
        )
        self.hacker_news_batch = HackerNewsHourly()

    def run(self):
        self.hacker_news_live_stories.run()
        self.hacker_news_batch.run(
            location="US",
            project=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id,
            credentials=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
        )

if __name__ == "__main__":
    app = L.LightningApp(HackerNewsDataProcesses())
