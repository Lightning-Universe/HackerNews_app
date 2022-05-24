import lightning as L
import pandas as pd
import streamlit as st
from lightning.utilities.state import AppState


def user_welcome(state: AppState):
    dummy_users = [None, "Marc", "Aniket", "Rohit", "Kaushik"]
    if not state.username:
        st.title("Welcome to HackerRec!")
        state.username = st.selectbox("Select user", dummy_users)
    else:
        st.title(f"Hey {state.username}, Here are your recommendations!")


def recommendations(state: AppState):
    data = {
        "Story Title": [
            """<a href='https://shopify.engineering/lessons-learned-apache-airflow-scale'>
            Lessons Learned from Running Apache Airflow at Scale</a>""",
            """<a href='https://blog.derhagen.eu/2022/05/23/im-quitting-my-phd.html'>
            I'm quitting my PhD (derhagen.eu)</a>""",
        ],
        "Category": ["Tech", "Sport"],
        "Created on": ["June 16th, 2022", "June 17th, 2022"],
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