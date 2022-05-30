import ast
import csv
import json
import random
import re
from collections import defaultdict

import numpy as np
import pandas as pd
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


if __name__ == "__main__":
    # get the config
    config = TANRConfig()

    # read the filtered data
    df = pd.read_csv("data/filtered_train.csv")

    # process the title
    df["title"] = (
        df["title"]
        .str.lower()
        .apply(lambda x: re.sub(r"""(?<=\w)([!?,.-:/"/'])""", r" \1 ", x))
        .apply(remove_space)
        .str.strip()
    )
    df = df.drop(["id", "id.1"], axis=1)

    # user fav distribution
    user_dist = (
        df.groupby("user_favorite")["pred_class"]
        .value_counts(normalize=True)
        .reset_index(name="dist")
        .pivot(index="user_favorite", columns="pred_class", values="dist")
        .fillna(0.0)
    )
    with open("data/user_topic_dist.json", "w") as fp:
        json.dump(user_dist.T.to_dict(), fp)

    least_fav = pd.melt(
        user_dist.reset_index(),
        id_vars=["user_favorite"],
        value_vars=[
            "Business",
            "Culture and Arts",
            "Education",
            "Entertainment",
            "Lifestyle",
            "News and Politics",
            "Sports",
            "Technology",
        ],
    )
    least_fav = least_fav.sort_values(by="value", ascending=False)
    least_fav = (
        least_fav.groupby("user_favorite")["pred_class"].apply(list).apply(lambda x: x[-config.least_fav_topic_count :])
    )
    with open("data/user_least_fav.json", "w") as fp:
        json.dump(least_fav.to_dict(), fp)

    # prepare data
    user_titles = df.groupby("user_favorite")["title"].apply(list).reset_index()
    final_data = []

    # sampling
    for i, row in tqdm(user_titles.head(2000).iterrows(), total=user_titles.shape[0]):
        pairs = []
        user = row["user_favorite"]
        titles = row["title"][-config.num_words_abstract :]  # TODO: take the most recent
        user_least_fav = least_fav[user]

        lfav_titles = df.loc[
            (df["user_favorite"] != user) & (df["pred_class"].isin(user_least_fav)),
            "title",
        ].sample(frac=1.0)
        lfav_titles_len = lfav_titles.shape[0]

        if lfav_titles_len < config.negative_sampling_ratio:
            continue

        for title_i, title in enumerate(titles):
            pair = [[title]]
            title_is = title_i % lfav_titles_len
            title_ie = title_is + config.negative_sampling_ratio
            browsed_news = titles[:title_i] + titles[title_i + 1 :]
            browsed_news = random.sample(browsed_news, len(browsed_news))

            pair[0].extend(lfav_titles.iloc[title_is:title_ie].tolist())
            pair.append(browsed_news)
            pairs.append(pair)

        final_data.append({"user": user, "candidate_news": pairs})

    final_data = pd.DataFrame(final_data).explode("candidate_news")
    final_data["browsed_news"] = final_data["candidate_news"].apply(lambda x: x[1])
    final_data["candidate_news"] = final_data["candidate_news"].apply(lambda x: x[0])
    final_data.to_csv("data/prepared_data.csv", header=True, index=False)
    final_data = pd.read_csv("data/prepared_data.csv")
    final_data["candidate_news"] = final_data["candidate_news"].apply(ast.literal_eval)
    final_data["browsed_news"] = final_data["browsed_news"].apply(ast.literal_eval)

    # tokenization
    word_freq = defaultdict(int)
    word2int = {}

    for titles in final_data["candidate_news"]:
        for title in titles:
            for word in title.split():
                word_freq[word] += 1

    for word in word_freq:
        if word_freq[word] >= config.word_freq_threshold:
            word2int[word] = len(word2int) + 1

    # prepare embeddings
    glove_path = "data/glove/glove.6B.300d.txt"
    source_embedding = pd.read_table(
        glove_path,
        index_col=0,
        sep=" ",
        header=None,
        quoting=csv.QUOTE_NONE,
        names=range(config.word_embedding_dim),
    )
    source_embedding = source_embedding.reset_index()
    source_embedding.columns = ["word"] + list(range(config.word_embedding_dim))
    word2int = pd.DataFrame(word2int.items(), columns=["word", "index"])
    final_embeddings = word2int.merge(source_embedding, how="left", on="word")
    orig_missed_embeddings = final_embeddings.loc[final_embeddings[0].isnull(), ["word", "index"]]
    final_embeddings = final_embeddings.loc[~final_embeddings[0].isnull()]

    missed_embeddings = pd.DataFrame(
        data=np.random.normal(size=(len(orig_missed_embeddings), config.word_embedding_dim)),
        index=orig_missed_embeddings["word"],
    ).reset_index()
    missed_embeddings = missed_embeddings.merge(orig_missed_embeddings, how="left", on="word")

    final_embeddings = pd.concat([final_embeddings, missed_embeddings])
    final_embeddings = final_embeddings.drop("word", axis=1)
    final_embeddings = final_embeddings.sort_values(by="index").drop("index", axis=1).values

    # save the embeddinfs
    np.save("data/final_embeddings.npy", final_embeddings)

    word2int = word2int.set_index("word")["index"].to_dict()
    with open("data/word2int.json", "w") as fp:
        json.dump(word2int, fp)

    final_data["candidate_news"] = final_data["candidate_news"].apply(
        lambda x: [tokenize(word, word2int) for word in x]
    )
    final_data["browsed_news"] = final_data["browsed_news"].apply(lambda x: [tokenize(word, word2int) for word in x])
    final_data = final_data.sample(frac=1.0)
    final_data = final_data.sort_values(by="user")
    final_data["user_ix"] = final_data.groupby("user").ngroup()
    unique_users = final_data["user_ix"].max() + 1
    val_split = int(unique_users * (1 - config.val_split_pct))

    final_data_train = final_data.loc[final_data["user_ix"] < val_split].reset_index(drop=True).drop("user_ix", axis=1)
    final_data_val = final_data.loc[final_data["user_ix"] >= val_split].reset_index(drop=True).drop("user_ix", axis=1)
    with open("data/tokenized_vectors_train.json", "w") as fp:
        json.dump(final_data_train.T.to_dict(), fp)

    with open("data/tokenized_vectors_val.json", "w") as fp:
        json.dump(final_data_val.T.to_dict(), fp)
