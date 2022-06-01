import lightning as L
import requests
import uvicorn

from hackernews_app.api.fastapi_app import app


class FastAPIServer(L.LightningWork):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_app_running = False

        # The url that requests will be made to.
        self.url = ""
        self.weights_path = None

    def run(self):
        uvicorn.run(app, host=self.host, port=self.port)
        if not self.url:
            self.url = f"http://{self.host}:{self.port}"

        if self.weights_path is None and self.url:
            # TODO: provide proper weights_path (@rohitgr7)
            weights_path = "ml/recsys/recsys_model_weights.ckpt"
            self.weights_path = weights_path
            requests.post(
                f"{self.server_one.url}/api/update_recsys_weights",
                headers={"X-Token": "hailhydra"},
                json={
                    "weights_path": weights_path,
                },
                timeout=10,
            )
