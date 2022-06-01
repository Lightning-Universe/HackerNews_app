import lightning as L

from ml.recsys.inference import generate_embeddings


class StoryEncoder(L.LightningWork):
    def __init__(self, weights_path):
        super().__init__()
        # TODO: provide proper weights_path (@rohitgr7)
        self.weights_path = "ml/recsys/recsys_model_weights.ckpt"
        self.embeddings = None

    def run(self, stories):
        embeddings = generate_embeddings(stories, self.weights_path)
        self.embeddings = L.storage.Payload(embeddings)
