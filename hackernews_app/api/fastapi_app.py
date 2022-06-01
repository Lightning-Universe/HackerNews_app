import json
import logging
import re
from typing import Dict

import numpy as np
import pandas as pd
from fastapi import FastAPI, Response, status

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

    Response:
    {
        results: [
            {
                title: STRING,
                url: STRING,
                topic: STRING,
                creation_date: STRING
            }
        ],
        type: "top"|"recommendation"
    }
    """

    global recsys_model
    user_vec = np.random.randn(300).tolist()
    stories = pd.DataFrame(
        {
            "title": ["This is a tech article"] * 100,
            "url": ["https://pytorch-lightning.readthedocs.io/en/stable/"] * 100,
            "topic": ["Tech"] * 100,
            "creation_date": ["2022-01-01"] * 100,
            "embed": [[0.234] * 300] * 100,
        }
    )
    story_vec = stories["embed"].tolist()
    stories["pred"] = get_click_prediction(user_vec, story_vec, recsys_model)
    stories = stories.sort_values(by="pred", ascending=False).head(50)
    stories = stories.drop(["pred", "embed"], axis=1)
    response = {
        "results": stories,
        "type": "recommendation",
    }
    return response


@app.post("/api/update_recsys_weights")
def update_model(payload: Dict):
    global recsys_model

    # TODO: Update the word2int here (@rohitgr7)
    with open("data/word2int.json") as fp:
        word2int = json.load(fp)

    config = TANRConfig()
    config.num_words = len(word2int) + 1  # PAD

    recsys_model = TANRModule.load_from_checkpoint(payload["weights_path"], config=config)
