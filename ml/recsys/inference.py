import json
import re

import pandas as pd
import torch

from config import TANRConfig
from ml.recsys.models.module import TANRModule

# In[2]:


spaces = [
    "\u200b",
    "\u200e",
    "\u202a",
    "\u202c",
    "\ufeff",
    "\uf0d8",
    "\u2061",
    "\x10",
    "\x7f",
    "\x9d",
    "\xad",
    "\xa0",
    "\u202f",
]


def remove_space(text):
    for space in spaces:
        text = text.replace(space, " ")
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text, word2int):
    res = []
    for word in text.split():
        if word in word2int:
            res.append(word2int[word])
    return res


def generate_embeddings(stories, weights_path):
    df = pd.DataFrame(stories)
    print(df)

    df["title"] = (
        df["title"]
        .str.lower()
        .apply(lambda x: re.sub(r"""(?<=\w)([!?,.-:/"/'])""", r" \1 ", x))
        .apply(remove_space)
        .str.strip()
    )

    with open("data/word2int.json") as fp:
        word2int = json.load(fp)

    df["title"] = df["title"].apply(lambda x: tokenize(x, word2int))
    df = df.loc[df["title"].apply(len) > 0]

    config = TANRConfig()
    config.num_words = len(word2int) + 1  # PAD

    candidate_news = df["title"].tolist()
    candidate_news = torch.tensor(
        [(news + [0] * config.num_words_title)[: config.num_words_title] for news in candidate_news]
    )
    candidate_news = {"title": candidate_news}
    embed_model = TANRModule.load_from_checkpoint(weights_path, config=config)

    news_embeddings = embed_model.get_news_vector(candidate_news).tolist()
    news_embeddings = [{"id": df["id"].iloc[i], "embeddings": embed} for i, embed in enumerate(news_embeddings)]
    return news_embeddings