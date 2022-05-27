import uuid

import pandas as pd
import requests
import streamlit as st
from lightning.utilities.state import AppState


def user_welcome(state: AppState):

    _prior_username = st.session_state.username

    st.image("visuals/hn.png", width=704)
    intro = st.container()

    if not st.session_state.username:
        intro.title("👋 Welcome to HackerRec!")
        intro.subheader("Personalized HackerNews stories for you based on your favorites ⚡️")
        st.session_state.username = intro.text_input(
            "Username", placeholder="Enter your HackerNews username (eg. AlexClay)"
        )
    else:
        recommendations(state)
        if (not st.session_state.user_status) and st.session_state.username:
            intro.subheader("Oops! :eyes:")
            intro.error(
                f"Could not find any recommendations for **{st.session_state.username}**."
                " The user either does not exist or does not have any favorites."
            )
            if intro.button("Want to try a different username?"):
                st.session_state.username = None
                st.session_state.user_status = False
        else:
            intro.title(f"👋 Hey {st.session_state.username}!")
            intro.subheader("Here are the personalized HackerNews stories for you! ⚡️")
            if intro.button("Use a different username"):
                st.session_state.username = None
                st.session_state.user_status = False

    if _prior_username != st.session_state.username:
        st.experimental_rerun()


@st.experimental_memo(show_spinner=False)
def get_user_recommendations(username: str, base_url: str):

    prediction = requests.post(
        f"{base_url}/api/recommend",
        headers={"X-Token": "hailhydra"},
        json={"username": username},
    )
    recommendations = prediction.json()["results"]
    if not recommendations:
        return

    df = pd.DataFrame(recommendations)
    df["title"] = df[["title", "url"]].apply(lambda x: f"<a href='{x[1]}'>{x[0]}</a>", axis=1)
    df = df.drop("url", axis=1).rename(
        columns={
            "title": "Story Title",
            "topic": "Category",
            "creation_date": "Created on",
        }
    )
    return df


def recommendations(state: AppState):
    if not st.session_state.username:
        return

    df = get_user_recommendations(st.session_state.username, state.server_one.url)

    if df is None:
        st.session_state.user_status = False
        return

    st.session_state.user_status = True

    unique_categories = df["Category"].unique()

    options = st.multiselect("Filter by categories of interest", unique_categories)

    if len(options) > 0:
        df = df.loc[df["Category"].isin(options)]

    hide_table_row_index = """
                <style>
                tbody th {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    # st.table(df)
    st.write(df.to_html(escape=False, index=False, justify="center"), unsafe_allow_html=True)


def home_ui(lightning_app_state):

    st.set_page_config(page_title="HackerNews App", page_icon="⚡️", layout="centered")

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid1().hex
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "user_status" not in st.session_state:
        st.session_state["user_status"] = False

    user_welcome(lightning_app_state)
