from typing import Dict

from google.cloud import bigquery
from fastapi import FastAPI, Response, status

from hackernews_app.contexts.secrets import LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS

app = FastAPI()
model = None

BQ_CREDENTIALS = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS
BQ_LOCATION = "US"
BQ_PROJECT = LIGHTNING__GCP_SERVICE_ACCOUNT_CREDS.project_id

@app.get("/healthz", status_code=status.HTTP_200_OK)
def healthz():
    return {"status": "ok"}


@app.post("/api/predict", status_code=status.HTTP_200_OK)
def predict(data: Dict, response: Response):
    """Requires a reference to a model and the materialized view that

    - batch train batch predict: query the warehouse
    - batch train, real-time inference
    TODO: look into DVC (https://dvc.org/) or feast (https://docs.feast.dev/).
    """

    user = data.get("user", None)

    if not user:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"data": "Requires a user, but user not found."}

    prediction = data

    return {"prediction": prediction}

