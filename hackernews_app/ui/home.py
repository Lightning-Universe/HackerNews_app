from typing import Dict, List

import lightning as L
import pandas as pd
import requests
import streamlit as st
from lightning.utilities.state import AppState

from config import HACKERNEWS_TOPICS_DATA, HACKERNEWS_USER_DATA


def user_welcome(state: AppState):
    users = [""] + list(requests.get(HACKERNEWS_USER_DATA).json().keys())
    if not state.username:
        st.title("Welcome to HackerRec!")
        state.username = st.selectbox("Select user", users)
    else:
        st.title(f"Hey {state.username}, Here are your recommendations!")


def get_story_data(username=None):
    response = requests.get(HACKERNEWS_TOPICS_DATA).json()
    titles, topics, created_dates = [], [], []
    user_data = None
    if username:
        user_data = get_user_data(username)

    for story_id, story_data in response.items():
        if not username or story_id in user_data:
            title = story_data["orig_title"]
            url = story_data["url"]
            topic = story_data["topic"]
            created_on = "24th May 2022"  # TODO: fetch date here
            titles.append(f"<a href='{url}'>{title}</a>")
            topics.append(topic)
            created_dates.append(created_on)

    data = {
        "Story Title": titles,
        "Category": topics,
        "Created on": created_dates,
    }
    df = pd.DataFrame(data)
    return df


def get_user_data(username: str) -> Dict[str, float]:
    users = requests.get(HACKERNEWS_USER_DATA).json()
    user: List[Dict[str, float]] = users[username]
    return {list(e.keys())[0]: list(e.values())[0] for e in user}


def recommendations(state: AppState):
    df = get_story_data(state.username)

    hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    # st.table(df)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)


def home_ui(lightning_app_state):
    user_welcome(lightning_app_state)
    recommendations(lightning_app_state)


class HackerNewsUI(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.username = None

    def configure_layout(self):
        return L.frontend.StreamlitFrontend(render_fn=home_ui)
