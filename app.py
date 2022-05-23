import lightning as L

from hackernews_app.flows.hacker_news_etl import HackerNewsETL
from hackernews_app.ui.home import HackerNewsUI


class HackerNewsApp(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.hacker_news_etl = HackerNewsETL()
        self.lit_streamlit = HackerNewsUI()

    def run(self):
        self.hacker_news_etl.run()

    def configure_layout(self):
        return {"name": "home", "content": self.lit_streamlit}


if __name__ == "__main__":
    app = L.LightningApp(HackerNewsApp())
