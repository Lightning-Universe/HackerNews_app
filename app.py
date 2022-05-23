import lightning as L

from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
from hackernews_app.flows import HackerNewsHourly, HackerNewsLiveStories
from hackernews_app.flows.model_serve import ModelServeFlow
from hackernews_app.ui.home import HackerNewsUI


class HackerNewsDataProcesses(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.hacker_news_live_stories = HackerNewsLiveStories(
            topic="hacker-news-items",
            location="US",
            project_id=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id,
        )
        self.hacker_news_batch = HackerNewsHourly()
        self.model_service = ModelServeFlow()
        self.lit_streamlit = HackerNewsUI()

    def run(self):
        self.model_service.run()
        self.hacker_news_live_stories.run(
            credentials=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
        )
        self.hacker_news_batch.run(
            location="US",
            project_id=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id,
            credentials=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS,
        )

    def configure_layout(self):
        return {"name": "home", "content": self.lit_streamlit}


if __name__ == "__main__":
    app = L.LightningApp(HackerNewsDataProcesses())
