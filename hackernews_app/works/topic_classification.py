from lightning import LightningWork

from ml.topic_classification.inference import predict as topic_predict


class TopicClassification(LightningWork):
    def __init__(self, weights_path):
        super().__init__()
        self.weights_path = weights_path

    def run(self, titles):
        return topic_predict(titles, self.weights_path)
