import lightning as L
from hackernews_app.flows.hacker_news_etl import HackerNewsETL

class HackerNewsApp(L.LightningFlow):

    def __init__(self):
        super().__init__()
        self.hacker_news_etl = HackerNewsETL()

    def run(self):
        print("Hello")
        self.hacker_news_etl.run()
        self._exit()


if __name__ == "__main__":
    app = L.LightningApp(HackerNewsApp())