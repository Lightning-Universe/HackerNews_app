from models.module import TANRModule
from datamodule.datamodule import TANRDataModule
from pytorch_lightning import Trainer, seed_everything
from config import TANRConfig
import numpy as np
import torch


if __name__ == '__main__':
    seed_everything(7)
    config = TANRConfig()
    pretrained_word_embeddings = np.load('data/final_embeddings.npy')
    pretrained_word_embeddings = torch.from_numpy(pretrained_word_embeddings)
    
    model = TANRModule(config, pretrained_word_embeddings=pretrained_word_embeddings)
    datamodule = TANRDataModule(config, train_data_path='data/tokenized_vectors_train.json', val_data_path='data/tokenized_vectors_val.json')
    trainer = Trainer(max_epochs=10)
    trainer.fit(model, datamodule=datamodule)