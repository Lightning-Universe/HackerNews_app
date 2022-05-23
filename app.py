import lightning as L

from hackernews_app.flows.hacker_news_etl import HackerNewsETL
from hackernews_app.ui.home import LitStreamlit


class HackerNewsApp(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.hacker_news_etl = HackerNewsETL()
        self.lit_streamlit = LitStreamlit()

    def run(self):
        print("Hello")
        self.hacker_news_etl.run()
        self._exit()

    def configure_layout(self):
        return {"name": "home", "content": self.lit_streamlit}


if __name__ == "__main__":
    app = L.LightningApp(HackerNewsApp())
