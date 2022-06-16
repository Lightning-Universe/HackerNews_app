import datetime as dt
import json
import re

import fsspec

# import fsspec
import pandas as pd
import torch

from config import TANRConfig
from ml.recsys.models.module import TANRModule

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
    """
    news_embeddings = torch.randn(df.shape[0], 300).tolist()
    created_time = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    news_embeddings = [
        {"story_id": df["id"].iloc[i], "embeddings": embed, "created_at": created_time}
        for i, embed in enumerate(news_embeddings)
    ]
    return news_embeddings
    """

    df["title"] = (
        df["title"]
        .str.lower()
        .apply(lambda x: re.sub(r"""(?<=\w)([!?,.-:/"/'])""", r" \1 ", x))
        .apply(remove_space)
        .str.strip()
    )

    with fsspec.open(
        "filecache::s3://pl-public-data/hackernews_app/word2int.json",
        s3={"anon": True},
        filecache={"cache_storage": "/tmp/files"},
    ) as fp:
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
    created_time = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    news_embeddings = [
        {"story_id": df["id"].iloc[i], "embeddings": embed, "created_at": created_time}
        for i, embed in enumerate(news_embeddings)
    ]
    return news_embeddings


def get_click_prediction(user_vec, story_vec, model):
    story_vec = torch.tensor(story_vec)
    user_vec = torch.tensor(user_vec)
    preds = model.get_prediction(story_vec, user_vec).sigmoid().tolist()
    return preds
