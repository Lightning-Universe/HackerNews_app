from torch import nn
from models.news_encoder import NewsEncoder
from models.user_encoder import UserEncoder
from models.dot_product import DotProductClickPredictor
import torch


class TANR(nn.Module):
    def __init__(self, config, pretrained_word_embedding=None):
        super().__init__()
        self.news_encoder = NewsEncoder(config, pretrained_word_embedding)
        self.user_encoder = UserEncoder(config)
        self.click_predictor = DotProductClickPredictor()

    def forward(self, candidate_news, browsed_news):
        """
        Args:
            candidate_news:
                [
                    {
                        "title": batch_size * num_words_title
                    } * (1 + K)
                ]
            browsed_news:
                [
                    {
                        "title": batch_size * num_words_title
                    } * num_clicked_news_a_user
                ]
        Returns:
            click_probability: batch_size, 1 + K
        """
        # batch_size, 1 + K, num_filters
        candidate_news_vector = torch.stack(
            [self.news_encoder(x) for x in candidate_news], dim=1)
        # batch_size, num_clicked_news_a_user, num_filters
        browsed_news_vector = torch.stack(
            [self.news_encoder(x) for x in browsed_news], dim=1)
        # batch_size, num_filters
        user_vector = self.user_encoder(browsed_news_vector)
        # batch_size, 1 + K
        click_probability = self.click_predictor(candidate_news_vector, user_vector)
        return click_probability