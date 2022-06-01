from unittest.mock import patch

from fastapi.testclient import TestClient

from hackernews_app.works.fastapi import app

client = TestClient(app)


def test_health():

    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_noroot():

    response = client.get("/")
    assert response.status_code == 404


@patch("google.cloud.bigquery.Client.query")
def test_recommend_status(mockquery):
    response = client.post("/api/recommend", json={"username": "eric"})

    # Establish that a query would've been executed.
    mockquery.assert_called()

    # Response code should be 200
    expected = 200
    actual = response.status_code
    assert expected == actual


@patch("google.cloud.bigquery.Client.query")
def test_recommend_dtypes(mockquery):
    response = client.post("/api/recommend", json={"username": "eric"})
    data = response.json()

    # Establish that a query would've been executed.
    mockquery.assert_called()

    # Results datatype is a list
    assert isinstance(data.get("results"), list)

    # Type field should be strings
    assert isinstance(data.get("type"), str)
