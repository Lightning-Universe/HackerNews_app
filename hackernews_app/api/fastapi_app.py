import datetime as dt
import json
import logging
import re
from typing import Dict

import fsspec
from fastapi import FastAPI, Response, status
from google.cloud import bigquery

from config import TANRConfig
from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
from ml.recsys.inference import get_click_prediction
from ml.recsys.models.module import TANRModule

logging.basicConfig(filename=f".{__name__}.log", format="%(filename)s: %(message)s", level=logging.INFO)

app = FastAPI()
recsys_model = None

BQ_CREDENTIALS = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
BQ_LOCATION = "US"
BQ_PROJECT = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id


@app.get("/healthz", status_code=status.HTTP_200_OK)
def healthz():
    return {"status": "ok"}


@app.post("/api/recommend", status_code=status.HTTP_200_OK)
def recommend(payload: Dict, response: Response):
    """Requires a reference to a model and the materialized view that.

    - batch train batch predict: query the warehouse
    - batch train, real-time inference
    TODO: look into DVC (https://dvc.org/) or feast (https://docs.feast.dev/).

    Returns:
    {
        results: [
            {
                title: STRING,
                url: STRING,
                topic: STRING,
                creation_date: STRING
            }
        ],
    }
    """

    username = payload["username"]
    user_embed_query = f"""
    with ranked_embeddings as (
        SELECT user_embeddings, rank() OVER (PARTITION BY username ORDER BY created_at desc) _rank
        FROM hacker_news.user_embeddings
        WHERE username = '{username}'
    )
    SELECT user_embeddings
    FROM ranked_embeddings
    WHERE _rank = 1;
    """

    new_stories_data = """
    SELECT se.story_id, se.embeddings, st.topic, si.title, si.time
    FROM hacker_news.story_embeddings se
    INNER JOIN hacker_news.story_topics st ON st.story_id = se.story_id
    INNER JOIN hacker_news.items si ON si.id = se.story_id
    ORDER BY se.created_at DESC
    LIMIT 100
    """

    client = bigquery.Client(BQ_PROJECT, credentials=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS)
    cursor = client.query(user_embed_query, location=BQ_LOCATION)
    user_vec = cursor.result().to_dataframe()

    if user_vec.shape[0] == 0:
        return {
            "results": None,
        }

    user_vec = user_vec["user_embeddings"].iloc[0]["embeddings"]

    cursor = client.query(new_stories_data, location=BQ_LOCATION)
    new_stories_df = cursor.result().to_dataframe()

    new_stories_df = new_stories_df.drop_duplicates(subset=["story_id"])
    new_stories_df = new_stories_df.rename(columns={"time": "creation_date"})
    new_stories_df["creation_date"] = new_stories_df["creation_date"].apply(
        lambda ts: dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    )
    new_stories_df["url"] = new_stories_df["story_id"].apply(lambda x: f"https://news.ycombinator.com/item?id={x}")
    new_stories_df = new_stories_df.drop("story_id", axis=1)

    story_vec = new_stories_df["embeddings"].tolist()

    global recsys_model
    new_stories_df["pred"] = get_click_prediction(user_vec, story_vec, recsys_model)
    new_stories_df = new_stories_df.sort_values(by="pred", ascending=False).head(50)
    new_stories_df = new_stories_df.drop(["pred", "embeddings"], axis=1)
    return {
        "results": new_stories_df,
    }


@app.post("/api/update_recsys_weights")
def update_model(payload: Dict):
    global recsys_model

    with fsspec.open(
        "filecache::s3://pl-public-data/hackernews_app/word2int.json",
        s3={"anon": True},
        filecache={"cache_storage": "/tmp/files"},
    ) as fp:
        word2int = json.load(fp)

    config = TANRConfig()
    config.num_words = len(word2int) + 1  # PAD

    recsys_model = TANRModule.load_from_checkpoint(payload["weights_path"], config=config)
