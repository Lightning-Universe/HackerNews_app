import datetime as dt

import lightning as L

from ml.topic_classification.inference import predict as topic_predict


class TopicClassification(L.LightningWork):
    def __init__(self, weights_path):
        super().__init__()
        # TODO: provide proper weights_path (@rohitgr7)
        self.weights_path = "ml/topic_classification/epoch=4-step=25110.ckpt"
        self.topics = None

    def run(self, stories):
        # topics = topic_predict([story["title"] for story in stories], self.weights_path)
        topics = ["Technology"] * len(stories)
        created_time = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        topics = [
            {"story_id": story["id"], "topic": topic, "created_at": created_time}
            for story, topic in zip(stories, topics)
        ]
        self.topics = L.storage.Payload(topics)
