import time

import lightning as L

from hackernews_app.flows.model_serve import ModelServeFlow
from hackernews_app.ui.app_starting import AppStarting
from hackernews_app.works.http import HTTPRequest


class HealthCheck(HTTPRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_healthy = False

    def get(self, url):
        if self.status_code == 200:
            self.is_healthy = True
        super().get(url)


class HackerNews(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.app_starting = AppStarting()
        self.model_service = ModelServeFlow()
        self.health_check = HealthCheck(run_once=False)

    def run(self):

        self.model_service.run()
        while self.health_check.is_healthy is False:
            self.health_check.get(f"{self.model_service.server_one.url}/healthz")
            time.sleep(1)

    def configure_layout(self):
        if self.health_check.is_healthy:
            return {"name": "Home", "content": self.model_service}
        else:
            return {"name": "Home", "content": self.app_starting}


if __name__ == "__main__":
    app = L.LightningApp(HackerNews())
