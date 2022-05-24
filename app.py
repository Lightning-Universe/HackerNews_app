import lightning as L

from hackernews_app.flows.model_serve import ModelServeFlow
from hackernews_app.ui.home import HackerNewsUI


class HackerNewsDataProcesses(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.model_service = ModelServeFlow()
        self.lit_streamlit = HackerNewsUI()

    def run(self):
        self.model_service.run()

    def configure_layout(self):
        return {"name": "home", "content": self.lit_streamlit}


if __name__ == "__main__":
    app = L.LightningApp(HackerNewsDataProcesses())
