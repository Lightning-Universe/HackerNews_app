from torch.utils.data import Dataset
import pandas as pd
import json
import torch


class TANRDataset(Dataset):
    def __init__(self, config, data_path):
        super().__init__()
        self.data_path = data_path
        self.config = config
        
        with open(data_path, 'r') as fp:
            self.user_data = json.load(fp)

    def __len__(self):
        return len(self.user_data)

    def __getitem__(self, idx):
        data = self.user_data[str(idx)]
        candidate_news = data['candidate_news']
        browsed_news = data['browsed_news']
        user = data['user']

        candidate_news = [{'title': torch.tensor((news + [0]*self.config.num_words_title)[:self.config.num_words_title])} for news in candidate_news]
        browsed_news = browsed_news[:self.config.num_clicked_news_a_user]
        browsed_news = [{'title': torch.tensor((news + [0]*self.config.num_words_title)[:self.config.num_words_title])} for news in browsed_news]
        missing_news_count = self.config.num_clicked_news_a_user - len(browsed_news)
        browsed_news = [{'title': torch.tensor([0] * self.config.num_words_title)}] * missing_news_count + browsed_news
        return {'user': user, 'candidate_news': candidate_news, 'browsed_news': browsed_news}


"""
browsed_news = [{'title': [fav11, fav21]}, {'title': [fav12, fav22]}, {'title': [fav13, fav23]}]
- we have to consider some min length here. No padding allowed in case user1 has 50 and user2 has 20
- there are not enough artiles, then push the padded tensor (pre-pad)

candidate = [{'title': [fav14, fav24]}, {'title': [nonfav15, nonfav25]}, {'title': [nonfav16, nonfav26]}]
targets = [1, 0, 0]

{'title': something, 'target': 1}

{
    'user': some_user,
    'target': [1, 0, 0]: (1+k)
    'candidate_news': [[news1_tensor], [news2_tensor], [news3_tensor]]: (1+k, title_length),
    'browsed_news': [[news5, tensor], [news6, tensor], ...]: (news_length, title_length)
}

{
    'target': (1+k),
    'candidate_news': 
}


candidate_news = [{'title': [1, 2, 3, 4]}, {'title': [4, 3, 2, 1]}]

candidate_news:
                [
                    {
                        "title": batch_size * num_words_title
                    } * (1 + K)
                ]
            clicked_news:
                [
                    {
                        "category": batch_size,
                        "title": batch_size * num_words_title
                    } * num_clicked_news_a_user
                ]

[1+k]
"""