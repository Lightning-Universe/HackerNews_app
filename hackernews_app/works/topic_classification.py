import requests
from lightning import LightningWork


class TopicClassification(LightningWork):
    def __init__(self, weights_path):
        super().__init__()
        self.weights_path = weights_path

    def run(self, stories):
        prediction = requests.post(
            f"{base_url}/api/predict_topic",
            headers={"X-Token": "hailhydra"},
            json={"username": stories, "weights_path": self.weights_path},
        )
        topics = prediction.json()["results"]
        return topics
