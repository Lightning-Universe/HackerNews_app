import numpy as np
import torch
from datamodule.datamodule import TANRDataModule
from models.module import TANRModule

from config import TANRConfig
from pytorch_lightning import seed_everything, Trainer

if __name__ == "__main__":
    seed_everything(7)
    config = TANRConfig()
    pretrained_word_embedding = np.load("data/final_embeddings.npy")
    pretrained_word_embedding = torch.from_numpy(pretrained_word_embedding)

    model = TANRModule(config, pretrained_word_embedding=pretrained_word_embedding)
    datamodule = TANRDataModule(
        config,
        train_data_path="data/tokenized_vectors_train.json",
        val_data_path="data/tokenized_vectors_val.json",
    )
    trainer = Trainer(max_epochs=config.num_epochs)
    trainer.fit(model, datamodule=datamodule)
