import datetime as dt

import lightning as L
from lightning.app.storage import Payload

from ml.topic_classification.inference import predict as topic_predict


class TopicClassification(L.LightningWork):
    def __init__(self, weights_path):
        super().__init__()
        self.weights_path = "https://pl-public-data.s3.amazonaws.com/hackernews_app/epoch=4-step=25110.ckpt"
        self.topics = None

    def run(self, stories):
        topics = topic_predict([story["title"] for story in stories], self.weights_path)
        created_time = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        topics = [
            {"story_id": story["id"], "topic": topic, "created_at": created_time}
            for story, topic in zip(stories, topics)
        ]
        self.topics = Payload(topics)
