import lightning as L
import pandas as pd
import streamlit as st
from lightning.utilities.state import AppState


def user_welcome(state: AppState):
    if not state.username:
        st.title("Welcome to HackerRec!")
        state.username = st.text_input("Username...")
    else:
        st.title(f"Hey {state.username}, Here are your recommendations!")


def recommendations(state: AppState):
    data = {
        "Story Title": [
            "Lightning.ai just released the biggest app",
            "Is baseball a real sport?",
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
    st.table(df)


def your_streamlit_app(lightning_app_state):
    user_welcome(lightning_app_state)
    recommendations(lightning_app_state)


class LitStreamlit(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.username = None

    def configure_layout(self):
        return L.frontend.StreamlitFrontend(render_fn=your_streamlit_app)
