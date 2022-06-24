from hackernews_app.api import constants, RESTAPI


class HackerNewsAPI(RESTAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(params=kwargs.get("params"), base_url=constants.HACKERNEWS_BASEURL)
