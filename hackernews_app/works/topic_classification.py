import lightning as L

from ml.topic_classification.inference import predict as topic_predict


class TopicClassification(L.LightningWork):
    def __init__(self, weights_path):
        super().__init__(parallel=True)
        # TODO: provide proper weights_path (@rohitgr7)
        self.weights_path = "ml/topic_classification/epoch=4-step=25110.ckpt"

    def run(self, stories):
        topics = topic_predict([story["title"] for story in stories], self.weights_path)
        topics = [{"id": story["id"], "topic": topic} for story, topic in zip(stories, topics)]
