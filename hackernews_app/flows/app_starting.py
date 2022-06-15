import lightning as L
from lightning.app.frontend.web import StaticWebFrontend


class AppStarting(L.LightningFlow):
    def configure_layout(self):
        return StaticWebFrontend(serve_dir="static/app_starting")
