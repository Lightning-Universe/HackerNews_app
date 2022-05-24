from typing import Dict
import json
import logging

from google.cloud import bigquery
from fastapi import FastAPI, Response, status

from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS

logging.basicConfig(filename=f'.{__name__}.log', format='%(filename)s: %(message)s', level=logging.INFO)

app = FastAPI()
model = None

BQ_CREDENTIALS = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
BQ_LOCATION = "US"
BQ_PROJECT = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id

@app.get("/healthz", status_code=status.HTTP_200_OK)
def healthz():
    return {"status": "ok"}


@app.post("/api/recommend", status_code=status.HTTP_200_OK)
def recommend(data: Dict, response: Response):
    """Requires a reference to a model and the materialized view that

    - batch train batch predict: query the warehouse
    - batch train, real-time inference
    TODO: look into DVC (https://dvc.org/) or feast (https://docs.feast.dev/).

    Ressponse:
    {
        username: x : STRING
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
        username
        , title
        , url
        , topic
        , cast(creation_date as string) creation_date
    from
        `hacker_news.v_lightningapp_hackernews_recommend`
    where
        username='{username}'
    order by
        ranking
    """

    hackernews_url = "https://news.ycombinator.com/item?id={item_id}"

    print(query)
    logging.info(f"User recommendation query: {query}")
    client = bigquery.Client(BQ_PROJECT, credentials=LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS)
    cursor = client.query(query, location=BQ_LOCATION)
    user_recommendation_df = cursor.result().to_dataframe()

    if user_recommendation_df.empty:
        print(f"No recommendation found for user {username}")
        response = {
            "username": username,
            "results": [],
            "type": "top",
        }

    else:
        _type = "top" if user_recommendation_df.empty else "recommendation"

        logging.info(f"User recommendation data frame return: {user_recommendation_df}")
        print(user_recommendation_df)
        response = user_recommendation_df.groupby("username").apply(
            lambda x: x[[col for col in user_recommendation_df.columns if col != "username"]].to_json(orient='records')
        ).to_dict()
        print(response)
        key = (*response,)[0]
        recommendations = json.loads(response.get(key, []))

        response = {
            "username": username,
            "results": recommendations,
            "type": _type,
        }

    return response
