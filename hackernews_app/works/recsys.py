import requests
from lightning import LightningWork


class RecSys(LightningWork):
    def __init__(self, model_weights):
        super().__init__()
        # TODO: Make the weights dynamic (@rohitgr7)
        self.model_weights = "https://pl-public-data.s3.amazonaws.com/hackernews_app/recsys_model_weights.ckpt"
        # call fastapi to update the weights
        requests.post(
            f"{base_url}/api/update_recsys_weights",
            headers={"X-Token": "hailhydra"},
            json={"weights_path": self.model_weights},
        )

    def run(self, user, story_ids):
        pass
