import lightning as L

from ml.recsys.inference import generate_embeddings


class StoryEncoder(L.LightningWork):
    def __init__(self, weights_path):
        super().__init__()
        self.weights_path = "https://pl-public-data.s3.amazonaws.com/hackernews_app/recsys_model_weights.ckpt"
        self.encodings = None

    def run(self, stories):
        encodings = generate_embeddings(stories, self.weights_path)
        self.encodings = L.storage.Payload(encodings)
