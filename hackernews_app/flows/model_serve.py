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

        # 1. A work is made aware of a new model getting deployed. (A work that listens for a new model)

        # 2. The work lets the flow know that there is a new deployment

        # 3. The flow creates an exact copy of the work that serves the model, except this time it will predict with the new model.
        #    The model servicing work needs to know the model and the features it needs.  So model and feature need to be
        #    parameterized.

        # 4. The flow runs both works.  It evaluates the scores from both models to determine which one is the winner.

        # 5. After a winner is decided the number of users getting served with the previous work decreases and is instead
        #    served with the new model.
