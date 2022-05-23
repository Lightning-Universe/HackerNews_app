import torch
from torch import optim, nn

from pytorch_lightning import LightningDataModule, LightningModule, Trainer
from models.tanr import TANR
from datamodule.dataset import TANRDataset
from torch.utils.data import DataLoader
from torchmetrics import Accuracy, AUROC, RetrievalNormalizedDCG, MetricCollection
import torch.nn.functional as F

class TANRModule(LightningModule):
    def __init__(self, config, pretrained_word_embeddings=None):
        super().__init__()
        self.config = config
        self.model = TANR(config, pretrained_word_embedding=None)

        metrics = MetricCollection({
            'acc': Accuracy(),
            'auroc': AUROC(),
        })
        self.train_metrics = metrics.clone(prefix='train_')
        self.valid_metrics = metrics.clone(prefix='val_')
        self.loss_fn = nn.CrossEntropyLoss()

    def training_step(self, batch, batch_idx):
        logits = self.model(batch['candidate_news'], batch['browsed_news'])
        targets = torch.zeros(logits.shape[0]).long().to(self.device)
        loss = self.loss_fn(logits, targets)
        targets = torch.zeros_like(logits).long()
        targets[..., 0] = 1
        logits = logits.view(-1).sigmoid()
        targets = targets.view(-1)
        metrics = self.train_metrics(logits, targets)
        self.log_dict(metrics, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        logits = self.model(batch['candidate_news'], batch['browsed_news'])
        targets = torch.zeros(logits.shape[0]).long().to(self.device)
        loss = self.loss_fn(logits, targets)
        targets = torch.zeros_like(logits).long()
        targets[..., 0] = 1
        logits = logits.view(-1).sigmoid()
        targets = targets.view(-1)
        metrics = self.valid_metrics(logits, targets)
        self.log('val_loss', loss, prog_bar=True)
        self.log_dict(metrics, prog_bar=True)

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=self.config.learning_rate)
        return optimizer

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

