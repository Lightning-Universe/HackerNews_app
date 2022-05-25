import pandas as pd
import requests
import streamlit as st
from lightning.utilities.state import AppState


def user_welcome(state: AppState):
    intro, logo = st.columns(2)

    if not state.username:
        intro.title("👋 Welcome to HackerRec!")
        intro.subheader("Personalized HackerNews stories for you ⚡️")
        state.username = intro.text_input("Enter username")
    elif (not state.user_status) and state.username:
        intro.subheader("Oops! :eyes:")
        intro.error(f"Could not find any recommendations for {state.username}.")
        if intro.button("Want to try a different username?"):
            state.username = None
            state.user_status = False
    else:
        intro.title(f"👋 Hey {state.username}!")
        intro.subheader("Here are the personalized HackerNews stories for you! ⚡️")
        if intro.button("Change username?"):
            state.username = None
            state.user_status = False

    logo.image("visuals/hn.jpeg", width=300)


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
    if not state.username:
        return

    df = get_user_recommendations(state.username, state.server_one.base_url)

    if df is None:
        state.user_status = False
        return

    state.user_status = True

    unique_categories = df["Category"].unique()
    options = st.multiselect("What are you interested in?", unique_categories)

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
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)


def home_ui(lightning_app_state):
    st.set_page_config(page_title="HackerNews App", page_icon="⚡️", layout="centered")
    user_welcome(lightning_app_state)
    recommendations(lightning_app_state)
