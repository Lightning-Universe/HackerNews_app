import torch
from models.additive import AdditiveAttention


class UserEncoder(torch.nn.Module):
    def __init__(self, config):
        super().__init__()
        self.additive_attention = AdditiveAttention(
            config.query_vector_dim, config.num_filters
        )

    def forward(self, clicked_story_vector):
        """
        Args:
            clicked_story_vector: batch_size, num_clicked_news_a_user, num_filters
        Returns:
            (shape) batch_size, num_filters
        """
        user_vector = self.additive_attention(clicked_story_vector)
        return user_vector
