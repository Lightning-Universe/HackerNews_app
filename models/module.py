import torch

from pytorch_lightning import LightningDataModule, LightningModule, Trainer
from models.tanr import TANR


class TANRDataModule(LightningDataModule):
    def __init__(self):
        super().__init__()

    def train_dataloader(self):
        pass

    def val_dataloader(self):
        pass

    def predict_dataloader(self):
        pass


class TANRModule(LightningModule):
    def __init__(self):
        super().__init__()
        self.model = TANR()

    def training_step(self, batch, batch_idx):
        pass

    def validation_step(self, batch, batch_idx):
        pass

    def predict_step(self, batch, batch_idx):
        pass

    def configure_optimizers(self):
        pass

    def get_news_vector(self, news):
        """
        Args:
            news:
                {
                    "title": batch_size * num_words_title
                }
        Returns:
            (shape) batch_size, num_filters
        """
        # batch_size, num_filters
        return self.model.news_encoder(news)

    def get_user_vector(self, browsed_news_vector):
        """
        Args:
            browsed_news_vector: batch_size, num_clicked_news_a_user, num_filters
        Returns:
            (shape) batch_size, num_filters
        """
        # batch_size, num_filters
        return self.model.user_encoder(browsed_news_vector)

    def get_prediction(self, news_vector, user_vector):
        """
        Args:
            news_vector: candidate_size, word_embedding_dim
            user_vector: word_embedding_dim
        Returns:
            click_probability: candidate_size
        """
        # candidate_size
        return self.model.click_predictor(
            news_vector.unsqueeze(dim=0),
            user_vector.unsqueeze(dim=0)).squeeze(dim=0)


if __name__ == '__main__':
    