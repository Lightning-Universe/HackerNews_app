import lightning as L
import uvicorn

from hackernews_app.api.fastapi_app import app


class FastAPIServer(L.LightningWork):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_app_running = False

        # The url that requests will be made to.
        self.url = ""

    def run(self):
        uvicorn.run(app, host=self.host, port=self.port, loop="asyncio")
        if not self.url:
            self.url = f"http://{self.host}:{self.port}"
