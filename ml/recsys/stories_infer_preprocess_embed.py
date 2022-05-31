#!/usr/bin/env python

# In[1]:


import json
import re

import numpy as np
import pandas as pd
import torch
from models.module import TANRModule
from tqdm.auto import tqdm

from config import TANRConfig

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


with open("data/word2int.json") as fp:
    word2int = json.load(fp)

config = TANRConfig()
pretrained_embeddings = np.load("data/final_embeddings.npy")
pretrained_embeddings = torch.from_numpy(pretrained_embeddings).float()


embed_model = TANRModule(config, pretrained_word_embedding=pretrained_embeddings)
embed_model.eval()


users = ["AlexClay", "HowardStark", "plibither8", "JimMorrison723", "NovaDev"]
fav_data = pd.read_csv("data/filtered_train.csv")
# fav_data = fav_data.loc[fav_data["user_favorite"].isin(users)]


fav_data = fav_data[["user_favorite", "title"]]

fav_data["title"] = (
    fav_data["title"]
    .str.lower()
    .apply(lambda x: re.sub(r"""(?<=\w)([!?,.-:/"/'])""", r" \1 ", x))
    .apply(remove_space)
    .str.strip()
)

fav_data["title"] = fav_data["title"].apply(lambda x: tokenize(x, word2int))

fav_data = fav_data.loc[fav_data["title"].apply(len) > 0]


fav_data = fav_data.groupby("user_favorite")["title"].apply(list).reset_index()

fav_data["title"] = fav_data["title"].apply(
    lambda x: [(news + [0] * config.num_words_title)[: config.num_words_title] for news in x]
)
fav_data["title"] = fav_data["title"].apply(lambda x: x[-config.num_words_abstract :])

fav_data["title"] = fav_data["title"].apply(
    lambda x: [[0] * config.num_words_title] * (config.num_clicked_news_a_user - len(x)) + x
)

user_vector = fav_data.set_index("user_favorite")["title"].to_dict()

user_embeddings = []

for i, (k, v) in tqdm(enumerate(user_vector.items())):
    v = {"title": torch.tensor(v)}
    with torch.inference_mode():
        browsed_news = embed_model.get_news_vector(v)[None]
        user_vec = embed_model.get_user_vector(browsed_news)[0]
        user_embeddings.append({"username": k, "user_embeddings": user_vec.tolist()})

with open("data/user_embeddings.json", "w") as fp:
    json.dump(user_embeddings, fp)
