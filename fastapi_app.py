import json
import logging
from typing import Dict

from fastapi import FastAPI, Response, status
from google.cloud import bigquery

from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
from ml.topic_classification.inference import predict as topic_predict

logging.basicConfig(filename=f".{__name__}.log", format="%(filename)s: %(message)s", level=logging.INFO)

app = FastAPI()

BQ_CREDENTIALS = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
BQ_LOCATION = "US"
BQ_PROJECT = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id


@app.get("/healthz", status_code=status.HTTP_200_OK)
def healthz():
    return {"status": "ok"}


@app.post("/api/recommend", status_code=status.HTTP_200_OK)
def recommend(data: Dict, response: Response):
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

    username = data.get("username", None)
    if not username:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"data": "Requires a user, but user not found."}

    query = f"""
    select
        title
        , url
        , topic
        , cast(creation_date as string) creation_date
    from
        `hacker_news.v_lightningapp_hackernews_recommend`
    where
        lower(username) = '{username.lower()}'
    order by
        ranking
    """

    logging.info(f"User recommendation query: {query}")
    client = bigquery.Client(BQ_PROJECT, credentials=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS)
    cursor = client.query(query, location=BQ_LOCATION)
    user_recommendation_df = cursor.result().to_dataframe()

    if user_recommendation_df.empty:
        response = {
            "results": [],
            "type": "top",
        }
    else:
        logging.info(f"User recommendation data frame return: {user_recommendation_df}")
        response = user_recommendation_df.to_json(orient="records")
        recommendations = json.loads(response)

        response = {
            "results": recommendations,
            "type": "recommendation",
        }

    return response


@app.post("/api/predict_topic", status_code=status.HTTP_200_OK)
def predict_topics(payload: Dict):
    return topic_predict(payload["stories"], payload["weights_path"])
