#!/usr/bin/env python

# In[1]:


import json
import pickle
import random
import re

import numpy as np
import pandas as pd
import torch
from models.module import TANRModule
from tqdm.auto import tqdm

from config import TANRConfig

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


# In[3]:


with open("data/new_stories.json") as fp:
    stories = json.load(fp)


# In[4]:


df = pd.DataFrame(stories)


# In[5]:


df["item_id"] = df["item_id"].astype(str)


# In[6]:


df = df[["item_id", "title"]]


# ### tokenization

# In[7]:


# df['orig_title'] = df['title'].copy()

df["title"] = (
    df["title"]
    .str.lower()
    .apply(lambda x: re.sub(r"""(?<=\w)([!?,.-:/"/'])""", r" \1 ", x))
    .apply(remove_space)
    .str.strip()
)


# In[8]:


with open("data/word2int.json") as fp:
    word2int = json.load(fp)


# In[9]:


df["title"] = df["title"].apply(lambda x: tokenize(x, word2int))


# In[10]:


df = df.loc[df["title"].apply(len) > 0]


# ### topic classification

# In[ ]:


# In[11]:


df["topic"] = "Sports"

CLASSES = [
    "Education",
    "Business",
    "Sports",
    "Technology",
    "News and Politics",
    "Lifestyle",
    "Culture and Arts",
    "Entertainment",
]

df["topic"] = df["topic"].apply(lambda x: random.sample(CLASSES, k=1)[0])


# In[12]:


topic_data = df[["item_id", "topic"]]


# In[13]:


topic_data.to_csv("data/topic_data_pred.tsv", sep="\t", header=True, index=False)

with open("data/topic_data_pred.pkl", "wb") as fp:
    pickle.dump(topic_data, fp)


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# In[ ]:


# ### generate embeddings

# In[14]:


# In[15]:


config = TANRConfig()
pretrained_embeddings = np.load("data/final_embeddings.npy")
pretrained_embeddings = torch.from_numpy(pretrained_embeddings).float()


# In[16]:


candidate_news = df["title"].tolist()
candidate_news = torch.tensor(
    [(news + [0] * config.num_words_title)[: config.num_words_title] for news in candidate_news]
)
candidate_news = {"title": candidate_news}


# In[17]:


embed_model = TANRModule(config, pretrained_word_embedding=pretrained_embeddings)


# In[18]:


news_vector = embed_model.get_news_vector(candidate_news)


# In[19]:


# news_vector = {df['item_id'].iloc[i]: vec for i, vec in enumerate(news_vector)}


# ### User data

# In[20]:


users = ["AlexClay", "HowardStark", "plibither8", "JimMorrison723", "NovaDev"]


# In[21]:


fav_data = pd.read_csv("data/filtered_train.csv")
# fav_data = fav_data.loc[fav_data["user_favorite"].isin(users)]
# fav_data["user_favorite"].value_counts()


# In[22]:


fav_data = fav_data[["user_favorite", "title"]]


# In[23]:


fav_data["title"] = (
    fav_data["title"]
    .str.lower()
    .apply(lambda x: re.sub(r"""(?<=\w)([!?,.-:/"/'])""", r" \1 ", x))
    .apply(remove_space)
    .str.strip()
)

fav_data["title"] = fav_data["title"].apply(lambda x: tokenize(x, word2int))

fav_data = fav_data.loc[fav_data["title"].apply(len) > 0]


# In[24]:


fav_data = fav_data.groupby("user_favorite")["title"].apply(list).reset_index()


# In[25]:


fav_data["title"] = fav_data["title"].apply(
    lambda x: [(news + [0] * config.num_words_title)[: config.num_words_title] for news in x]
)
fav_data["title"] = fav_data["title"].apply(lambda x: x[-config.num_words_abstract :])


# In[26]:


fav_data["title"] = fav_data["title"].apply(
    lambda x: [[0] * config.num_words_title] * (config.num_clicked_news_a_user - len(x)) + x
)


# In[27]:


user_vector = fav_data.set_index("user_favorite")["title"].to_dict()


preds = {}

for k, v in tqdm(user_vector.items()):
    v = {"title": torch.tensor(v)}
    browsed_news = embed_model.get_news_vector(v)[None]
    user_vec = embed_model.get_user_vector(browsed_news)[0]
    preds[k] = embed_model.get_prediction(news_vector, user_vec).sigmoid().tolist()
    preds[k] = [[df.iloc[i]["item_id"], prob] for i, prob in enumerate(preds[k])]
    preds[k] = sorted(preds[k], key=lambda x: -x[1])[:10]


preds = pd.DataFrame(preds).T.reset_index()
preds = preds.rename(columns={"index": "username"})
cols = list(range(10))
preds["story_id"] = preds[cols].apply(lambda x: x.tolist(), axis=1)
preds = preds.drop(cols, axis=1)
preds = preds.explode("story_id").reset_index(drop=True)
preds["score"] = preds["story_id"].apply(lambda x: x[1])
preds["story_id"] = preds["story_id"].apply(lambda x: x[0])


preds.to_csv("data/new_stories_user_pred.tsv", sep="\t", header=True, index=False)

with open("data/new_stories_user_pred.pkl", "wb") as fp:
    pickle.dump(preds, fp)
