import time

import lightning as L
import requests

from hackernews_app.flows.model_serve import ModelServeFlow
from hackernews_app.ui.app_starting import AppStarting


class HackerNews(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.app_starting = AppStarting()
        self.model_service = ModelServeFlow()

    def run(self):
        self.model_service.run()

        # TODO: check why this doesn't work in fastapi (@rohitgr7)
        if not self.model_service.server_one.is_running:
            while requests.get(f"{self.model_service.server_one.url}/healthz").status_code != 200:
                time.sleep(1)

            self.model_service.server_one.is_running = True

    def configure_layout(self):
        if self.model_service.server_one.is_running:
            return {"name": "Home", "content": self.model_service}
        else:
            return {"name": "Home", "content": self.app_starting}


if __name__ == "__main__":
    app = L.LightningApp(HackerNews())
