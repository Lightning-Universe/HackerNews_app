import lightning as L

from hackernews_app.ui.home import home_ui
from hackernews_app.works.fastapi import FastAPIServer


class ModelServeFlow(L.LightningFlow):
    """This flow configures the FastAPI and serving UI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.server_one = FastAPIServer(parallel=True)
        self.is_app_running = False

    def run(self):
        self.server_one.run()
        self.is_app_running = True

    def configure_layout(self):
        return L.frontend.StreamlitFrontend(render_fn=home_ui)
