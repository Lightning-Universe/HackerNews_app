import torch


class DotProductClickPredictor(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, candidate_story_vector, user_vector):
        """
        Args:
            candidate_story_vector: batch_size, candidate_size, X
            user_vector: batch_size, X
        Returns:
            (shape): batch_size
        """
        # batch_size, candidate_size
        probability = torch.bmm(
            candidate_story_vector, user_vector.unsqueeze(dim=-1)
        ).squeeze(dim=-1)
        return probability
