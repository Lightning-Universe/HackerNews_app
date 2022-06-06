import fsspec
import numpy as np
import torch

from config import TANRConfig
from ml.recsys.datamodule.datamodule import TANRDataModule
from ml.recsys.models.module import TANRModule
from pytorch_lightning import seed_everything, Trainer

if __name__ == "__main__":
    seed_everything(7)
    config = TANRConfig()

    with fsspec.open(
        "filecache::s3://pl-public-data/hackernews_app/final_embeddings.npy",
        s3={"anon": True},
        filecache={"cache_storage": "/tmp/files"},
    ) as fp:
        pretrained_word_embedding = np.load(fp)

    pretrained_word_embedding = torch.from_numpy(pretrained_word_embedding).float()

    model = TANRModule(config, pretrained_word_embedding=pretrained_word_embedding)
    datamodule = TANRDataModule(
        config,
        train_data_path="s3://pl-public-data/hackernews_app/tokenized_vectors_train.json",
        val_data_path="s3://pl-public-data/hackernews_app/tokenized_vectors_val.json",
    )
    trainer = Trainer(max_epochs=config.num_epochs)
    trainer.fit(model, datamodule=datamodule)
