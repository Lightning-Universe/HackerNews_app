import lightning as L


class HackerNewsETL(L.LightningFlow):
    def __init__(self):
        super().__init__()
