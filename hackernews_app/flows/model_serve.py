import lightning as L
import requests

from hackernews_app.works.fastapi import FastAPIServer


class ModelServe(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.server = FastAPIServer(parallel=True)
        self.weights_path = None

    def run(self):
        self.server.run()
        print("run tests")

        if self.weights_path is None and self.server.url:
            # TODO: provide proper weights_path (@rohitgr7)
            weights_path = "https://pl-public-data.s3.amazonaws.com/hackernews_app/recsys_model_weights.ckpt"
            self.weights_path = weights_path
            requests.post(
                f"{self.server.url}/api/update_recsys_weights",
                headers={"X-Token": "hailhydra"},
                json={
                    "weights_path": weights_path,
                },
                timeout=10,
            )
