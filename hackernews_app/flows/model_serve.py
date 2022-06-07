import lightning as L

from hackernews_app.ui.home import home_ui
from hackernews_app.works.fastapi import FastAPIServer


class ModelServeFlow(L.LightningFlow):
    """This flow configures the FastAPI and serving UI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.server_one = FastAPIServer(parallel=True)

    def run(self):
        self.server_one.run()

    def configure_layout(self):
        return L.frontend.StreamlitFrontend(render_fn=home_ui)
