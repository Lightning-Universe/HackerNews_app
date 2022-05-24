import lightning as L

from hackernews_app.works.model_serve import FastAPIWork

class ModelServeFlow(L.LightningFlow):
    """This flow decides which model to use.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.server_one = FastAPIWork(module="fastapi_app", api_object="app")

    def run(self):

        if not self.server_one.has_started:
            self.server_one.run()
