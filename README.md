## Installation
### Local Development
```shell
# If ~/.lightning.secrets/.secrets.json does not exist
mkdir ~/.lightning.secrets/

touch ~/.lightning.secrets/.secrets.json
# From the hackernews 1Password vault, copy the credentials from gcp-grid-analytics-processes-prod-sa into ~/.lightning.secrets/.secrets.json

git clone git@github.com:PyTorchLightning/hackernews-app.git
cd hackernews-app
pip install -r requirements.txt
lightning run app app.py
```

## HackerNews App

![Model](./visuals/model.png)

**. Terminology:**

1. Browsed News: Stories from the favorites API.
1. Candidate News:
   1. Positive Samples: Favorites API
   1. Negative Samples: Stories from different topics
1. News Encoder: Will run on each story

### User journey:

1. We will already store the embeddings of the new stories (per day)
1. User enters their username on the UI, gets the recommendations
1. Real-time, run the click predictor on the new stories embeddings and user embeddings and show the ranked results.

