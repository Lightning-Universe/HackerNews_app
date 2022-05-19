from math import sqrt

import torch
import torch.nn as nn


class DNNClickPredictor(torch.nn.Module):
    def __init__(self, input_size, hidden_size=None):
        super().__init__()
        if hidden_size is None:
            hidden_size = int(sqrt(input_size))
        self.dnn = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1),
        )

    def forward(self, candidate_story_vector, user_vector):
        """
        Args:
            candidate_story_vector: batch_size, X
            user_vector: batch_size, X
        Returns:
            (shape): batch_size
        """
        # batch_size
        return self.dnn(
            torch.cat((candidate_story_vector, user_vector), dim=1)
        ).squeeze(dim=1)
