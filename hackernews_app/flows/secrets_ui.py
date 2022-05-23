import json
import os
import logging

import streamlit as st

import lightning as L
from lightning.frontend import StreamlitFrontend
from lightning.utilities.state import AppState

from pathlib import Path


def write_configs(data):

    filepath = Path(os.path.join(str(Path.home()), ".secrets.json"))
    with open(filepath, "w") as f:
        json.dump(data, f)

def read_configs():

    try:
        filepath = Path(os.path.join(str(Path.home()), ".secrets.json"))
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Could not find {filepath}.")
        return None
    except json.decoder.JSONDecodeError:
        logging.error(f"Secrets file {filepath} is not in valid JSON format.")
        return None

class BigQuerySecretsUI(L.LightningFlow):
    """The interface that a user inputs configurations and gets log information."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.secrets = read_configs()

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state: AppState):

    col1, col2 = st.columns(2)

    with col1:
        st.title("Secrets")
        if state.secrets:

            st.write("Secrets that have been loaded.")
            for key in state.secrets.keys():
                st.code(key)
        else:
            st.write("Please add the GCP service account credentials that will be used to access BigQuery.")


    with col2:
        bq_secrets_key = st.text_input("Reference tag for the secret.", value="GCP_SERVICE_ACCOUNT_CREDS")
        bq_secrets_value = st.text_input("Google Cloud Service Account Key Used to Access BigQuery", type="password")

        save_notification_settings = st.button("Save Secrets.")
        if save_notification_settings:

            try:
                secrets = json.loads(bq_secrets_value)
                state.secrets = {bq_secrets_key: secrets}
                st.write(f"Loaded keys for GCP Service Account")
                write_configs(secrets)
            except json.decoder.JSONDecodeError:
                st.write("Unable to save the secrets. Expected a JSON string")

