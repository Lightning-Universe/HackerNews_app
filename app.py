import time

import lightning as L

from hackernews_app.flows.model_serve import ModelServeFlow
from hackernews_app.ui.app_starting import AppStarting
from hackernews_app.works.http import HTTPRequest


class HackerNews(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.app_starting = AppStarting()

        # This is just
        self.model_service = ModelServeFlow()

        # Checks that the FastAPI service is availabe.
        self.health_check = HealthCheck()

    def run(self):
        self.model_service.run()

        # Check every second until the FastAPI service gives a response.
        if self.health_check.is_healthy is False:
            self.health_check.get(f"{self.model_service.server_one.url}/healthz")
            time.sleep(1)

    def configure_layout(self):
        # When the health check is successful.
        if self.health_check.is_healthy:
            return {"name": "Home", "content": self.model_service}
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
