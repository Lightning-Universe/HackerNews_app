import lightning as L
import pandas as pd
import requests
import streamlit as st
from lightning.utilities.state import AppState

from config import HACKERNEWS_API


def user_welcome(state: AppState):
    dummy_users = [None, "Marc", "Aniket", "Rohit", "Kaushik"]
    if not state.username:
        st.title("Welcome to HackerRec!")
        state.username = st.selectbox("Select user", dummy_users)
    else:
        st.title(f"Hey {state.username}, Here are your recommendations!")


def recommendations(state: AppState):
    response = requests.get(HACKERNEWS_API).json()
    titles, topics, created_dates = [], [], []
    for id, story_data in response.items():
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
