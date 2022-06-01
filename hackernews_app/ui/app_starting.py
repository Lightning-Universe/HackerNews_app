import lightning as L


class AppStarting(L.LightningFlow):
    def configure_layout(self):
        return L.frontend.web.StaticWebFrontend(serve_dir="static/app_starting")
