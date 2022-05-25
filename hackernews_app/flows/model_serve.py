import lightning as L

from hackernews_app.ui.home import home_ui
from hackernews_app.works.model_serve import FastAPIWork


class ModelServeFlow(L.LightningFlow):
    """This flow decides which model to use."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.server_one = FastAPIWork(module="fastapi_app", api_object="app")
        self.username = None
        self.user_status = False

    def run(self):
        if not self.server_one.has_started:
            self.server_one.run()

    def configure_layout(self):
        return L.frontend.StreamlitFrontend(render_fn=home_ui)
