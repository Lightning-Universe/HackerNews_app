import lightning as L
import streamlit as st


def your_streamlit_app(lightning_app_state):
    st.write('hello world')


class LitStreamlit(L.LightningFlow):
    def configure_layout(self):
        return L.frontend.StreamlitFrontend(render_fn=your_streamlit_app)
