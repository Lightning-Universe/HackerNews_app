import uuid

import lightning as L
import pandas as pd
import requests
import streamlit as st
from lightning.app.frontend import StreamlitFrontend
from lightning.app.utilities.state import AppState


class HackerNewsUI(L.LightningFlow):
    def __init__(self):
        super().__init__()
        # Define required states for multiple user sessions
        self.multi_user_states = {
            "username": None,
            "user_status": False,
            "page_number": 0,
        }
        self.fastapi_url = None
        # Number of entries per page for the recommendation table
        self.num_entries_per_page = 15

    def run(self, fastapi_url):
        self.fastapi_url = fastapi_url

    def configure_layout(self):
        return StreamlitFrontend(render_fn=hackernews_streamlit)


TEXT_ELEMENTS = {
    # Text for the home page.
    "welcome_title": "👋 Welcome to HackerRec!",
    "welcome_subheader": "Personalized HackerNews stories for you based on your favorites ⚡️",
    "text_input_placeholder": "Enter your HackerNews username (eg. AlexClay)",
    # Text for the error message when the user does not exist or does not have any favorites.
    "not_found_error_subheader": "Oops! :eyes:",
    "not_found_error_message": "Could not find any recommendations for **{username}**. The user either does not exist or does not have any favorites.",
    "not_found_error_try_different_username": "Want to try a different username?",
    # Text when the user is logged in.
    "user_welcome_title": "👋 Hey {username}!",
    "user_welcome_subheader": "Here are the personalized HackerNews stories for you! ⚡️",
    "user_welcome_try_different_username": "Use a different username",
}


def hackernews_streamlit(lightning_app_state):

    # Set HackerNews App page config here
    st.set_page_config(page_title="HackerNews App", page_icon="⚡️", layout="centered")

    # Define session states for multiple users
    set_session_states_for_multi_users(**lightning_app_state.multi_user_states)

    # Home page render logic
    home_page(lightning_app_state, TEXT_ELEMENTS)


def set_session_states_for_multi_users(**kwargs):
    """Set session states for multiple users."""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid1().hex

    for key, value in kwargs.items():
        if key not in st.session_state:
            st.session_state[key] = value


def home_page(state: AppState, text_elements: dict):
    """There are three main pages in this app:

    1. Welcome page
    2. Error page when the user does not exist or does not have any favorites
    3. User page when the user is logged in and with recommendations table
    """

    _prior_username = st.session_state.username

    st.image("visuals/hn.png", width=704)
    intro = st.container()

    if not st.session_state.username:
        intro.title(text_elements["welcome_title"])
        intro.subheader(text_elements["welcome_subheader"])
        st.session_state.username = intro.text_input("Username", placeholder=text_elements["text_input_placeholder"])
    else:
        recommendations_table(state)
        if (not st.session_state.user_status) and st.session_state.username:
            intro.subheader(text_elements["not_found_error_subheader"])
            intro.error(f"{text_elements['not_found_error_message'].format(username=st.session_state.username)}")
            if intro.button(text_elements["not_found_error_try_different_username"]):
                st.session_state.username = None
                st.session_state.user_status = False
        else:
            intro.title(f"{text_elements['user_welcome_title'].format(username=st.session_state.username)}")
            intro.subheader(text_elements["user_welcome_subheader"])
            if intro.button(text_elements["user_welcome_try_different_username"]):
                st.session_state.username = None
                st.session_state.user_status = False

    if _prior_username != st.session_state.username:
        st.experimental_rerun()


def recommendations_table(state: AppState):
    """Render the recommendations table.

    +------------------------------------+-------------+---------------------+
    | Story Title                        | Category    | Created on          |
    +====================================+=============+=====================+
    | HackerNews App for recommendations | Technology  | 1st June, 2022      |
    +------------------------------------+-------------+---------------------+

    TODO (@kaushikb11): Make the recommendations table prettier ;)
    """
    if not st.session_state.username:
        return

    df = get_user_recommendations(st.session_state.username, state.fastapi_url)

    if df is None:
        st.session_state.user_status = False
        return

    st.session_state.user_status = True

    unique_categories = df["Category"].unique()

    options = st.multiselect("Filter by categories of interest", unique_categories)

    if len(options) > 0:
        df = df.loc[df["Category"].isin(options)]

    last_page = len(df) // state.num_entries_per_page

    # Add a next button and a previous button
    prev, _, next = st.columns([1, 10, 1])

    if next.button("Next"):
        if st.session_state.page_number + 1 > last_page:
            st.session_state.page_number = 0
        else:
            st.session_state.page_number += 1

    if prev.button("Previous"):
        if st.session_state.page_number - 1 < 0:
            st.session_state.page_number = last_page
        else:
            st.session_state.page_number -= 1

    # Get start and end indices of the next page of the dataframe
    start_idx = st.session_state.page_number * state.num_entries_per_page
    end_idx = (1 + st.session_state.page_number) * state.num_entries_per_page

    # Index into the sub dataframe
    sub_df = df.iloc[start_idx:end_idx]

    hide_table_row_index = """
        <style>
        tbody th {display:none}
        .blank {display:none}
        </style>
        """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    st.write(sub_df.to_html(escape=False, index=False, justify="center"), unsafe_allow_html=True)


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
