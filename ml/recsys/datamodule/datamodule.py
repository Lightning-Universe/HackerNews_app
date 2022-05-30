from datamodule.dataset import TANRDataset
from torch.utils.data import DataLoader

from pytorch_lightning import LightningDataModule


class TANRDataModule(LightningDataModule):
    def __init__(self, config, train_data_path, val_data_path):
        super().__init__()
        self.config = config
        self.train_data_path = train_data_path
        self.val_data_path = val_data_path

    def setup(self, stage):
        if stage == "fit":
            self.train_ds = TANRDataset(self.config, self.train_data_path)
            self.val_ds = TANRDataset(self.config, self.val_data_path)

    def train_dataloader(self):
        return DataLoader(
            self.train_ds,
            batch_size=self.config.batch_size,
            num_workers=self.config.num_workers,
            shuffle=True,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_ds,
            batch_size=self.config.batch_size,
            num_workers=self.config.num_workers,
            shuffle=False,
        )
