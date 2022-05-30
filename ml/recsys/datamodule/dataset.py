import json

import torch
from torch.utils.data import Dataset


class TANRDataset(Dataset):
    def __init__(self, config, data_path):
        super().__init__()
        self.data_path = data_path
        self.config = config

        with open(data_path) as fp:
            self.user_data = json.load(fp)

    def __len__(self):
        return len(self.user_data)

    def __getitem__(self, idx):
        data = self.user_data[str(idx)]
        candidate_news = data["candidate_news"]
        browsed_news = data["browsed_news"]
        user = data["user"]

        candidate_news = [
            {"title": torch.tensor((news + [0] * self.config.num_words_title)[: self.config.num_words_title])}
            for news in candidate_news
        ]
        browsed_news = browsed_news[: self.config.num_clicked_news_a_user]
        browsed_news = [
            {"title": torch.tensor((news + [0] * self.config.num_words_title)[: self.config.num_words_title])}
            for news in browsed_news
        ]
        missing_news_count = self.config.num_clicked_news_a_user - len(browsed_news)
        browsed_news = [{"title": torch.tensor([0] * self.config.num_words_title)}] * missing_news_count + browsed_news
        return {
            "user": user,
            "candidate_news": candidate_news,
            "browsed_news": browsed_news,
        }
