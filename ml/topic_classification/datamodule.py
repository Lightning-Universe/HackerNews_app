import os

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer

from config import TopicClassificationConfig
from pytorch_lightning import LightningDataModule


class NewsDataset(Dataset):
    def __init__(self, df, tokenizer, max_length):
        super().__init__()
        self.df = df
        self.tokenizer = tokenizer
        self.max_length = max_length
        config = TopicClassificationConfig()
        self.classes_to_ix = {cl: i for i, cl in enumerate(config.classes)}

    def __len__(self):
        return self.df.shape[0]

    def __getitem__(self, idx):
        text, category = self.df[["text", "category"]].iloc[idx]
        encoded_text = self.tokenizer.encode_plus(
            text, truncation=True, add_special_tokens=True, max_length=self.max_length, padding="max_length"
        )

        category_ix = self.classes_to_ix[category]

        input_ids, attention_mask = encoded_text["input_ids"], encoded_text["attention_mask"]

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "target": torch.tensor(category_ix, dtype=torch.long),
        }


class NewsDatasetPredict(Dataset):
    def __init__(self, df, tokenizer, max_length):
        super().__init__()
        self.df = df
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return self.df.shape[0]

    def __getitem__(self, idx):
        text = self.df["title"].iloc[idx]
        encoded_text = self.tokenizer.encode_plus(
            text, truncation=True, add_special_tokens=True, max_length=self.max_length, padding="max_length"
        )

        input_ids, attention_mask = encoded_text["input_ids"], encoded_text["attention_mask"]

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        }


class NewsClassificationDataModule(LightningDataModule):
    def __init__(self, df, model_name, val_split=0.2):
        super().__init__()
        self.df = df
        self.model_name = model_name
        self.val_split = val_split

    def setup(self, stage):
        # TODO: Try to store this in artifacts (@rohitgr7)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        if stage == "predict":
            self.predict_dataset = NewsDatasetPredict(self.df, tokenizer, max_length=200)
        elif stage == "fit":
            split_idx = int(self.df.shape[0] * self.val_split)
            val_df, train_df = self.df.iloc[:split_idx], self.df.iloc[split_idx:]
            self.train_dataset = NewsDataset(train_df, tokenizer, max_length=200)
            self.val_dataset = NewsDataset(val_df, tokenizer, max_length=200)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=32, shuffle=True, num_workers=os.cpu_count())

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=32, shuffle=False, num_workers=os.cpu_count())

    def predict_dataloader(self):
        return DataLoader(self.predict_dataset, batch_size=32, shuffle=False, num_workers=os.cpu_count())
