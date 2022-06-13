import os
import time

import lightning as L

from hackernews_app.flows import AppStarting, HackerNewsUI
from hackernews_app.flows.hacker_news_live import HackerNewsLiveStories
from hackernews_app.works.fastapi import FastAPIServer
from hackernews_app.works.http import HTTPRequest


class HackerNews(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.app_starting = AppStarting()
        self.server = FastAPIServer(parallel=True)
        self.hackernews_ui = HackerNewsUI()
        self.health_check = HealthCheck(cache_calls=False)
        self.hn_live_stream = HackerNewsLiveStories(topic="hn_stream", time_interval=5)

    def run(self):
        self.hn_live_stream.run()
        if os.environ.get("LAI_TEST"):
            print("⚡ Lightning HackerNews App! ⚡")

        self.server.run()

        # Wait for the fastapi server to start before launching the UI
        if self.health_check.is_healthy is False:
            if self.server.url:
                self.health_check.get(f"{self.server.url}/healthz")
            print("Waiting for the server to start.....")
            time.sleep(1)
        else:
            self.hackernews_ui.run(self.server.url)

    def configure_layout(self):
        # When the health check is successful.
        if self.health_check.is_healthy:
            return {"name": "Home", "content": self.hackernews_ui}
        else:
            return {"name": "Home", "content": self.app_starting}


class HealthCheck(HTTPRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_healthy = False

    def get(self, url):
        if self.status_code == 200:
            self.is_healthy = True
        super().get(url)


if __name__ == "__main__":
    app = L.LightningApp(HackerNews())
