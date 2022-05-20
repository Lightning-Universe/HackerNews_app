import time
import datetime as dt
import logging
import pickle
import lightning as L
from hackernews_app.works.hacker_news import HackerNewsGetItem, HackerNewsSubscriber, HackerNewsRequestAPI

from hackernews_app.api.hackernews import constants
from lightning_gcp.bigquery import BigQueryWork


logging.basicConfig(level=logging.INFO)

class HackerNewsLiveStories(L.LightningFlow):
    """ This flow runs endlessly

    """

    def __init__(
        self,
        project_id: str,
        topic: str,
        time_interval: int = 5,
    ):
        super().__init__()
        self.time_interval = time_interval
        self.item_getter = HackerNewsGetItem(project_id, topic, run_once=False)
        self.subscriber = HackerNewsSubscriber(
            project_id=project_id,
            topic_name=self.item_getter.topic_name,
            subscription="hacker-news-items-subscription",
            run_once=False
        )

    def run(self):

        if self.item_getter.data:
            self.subscriber.run()
        # The property of the work isn't changing
        else:
            self.item_getter.run()
        logging.info(f"getter data: {self.item_getter.data}")

        logging.info(f"subscriber: {self.subscriber.messages}")
        if self.item_getter.has_started:
            return

        time.sleep(self.time_interval)


class LastGroupLoader(L.LightningWork):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.last_group = None

    def run(self, filepath: str):
        last_group = pickle.load(open(filepath, 'rb'))
        self.last_group = int(last_group.maxvalue.iloc[0]) + 1 if len(last_group) else 1

class HackerNewsHourly(L.LightningFlow):

    def __init__(self):
        super().__init__()
        self.should_execute = True #TODO: change this to False

        # Run one time to get the data we need.
        self.last_group_getter = BigQueryWork(run_once=True)
        self.last_group_loader = LastGroupLoader(run_once=True)

        # Recurring runs
        self.api_client = HackerNewsRequestAPI()
        self.inserter = BigQueryWork(run_once=False)
        self.to_insert = True


    def run(self, project, location, credentials):

        if self.last_group_loader.last_group is None:

            query = """
                select coalesce(max(group_id), 1) maxvalue
                from `hacker_news.top_stories`
            """

            self.last_group_getter.run(
                query=query,
                project=project,
                location=location,
                credentials=credentials,
                to_dataframe=True,
            )

        if self.last_group_getter.has_succeeded:
            self.last_group_loader.run(self.last_group_getter.result_path)

        # Start recurring loop.

        if self.schedule("* * * * *"):#"hourly"):
            self.should_execute = True

        if self.should_execute is False:
            return

        # Get data
        self.api_client.run(constants.HACKERNEWS_TOP_STORIES_ENDPOINT)
        logging.info(self.api_client.response_data)

        if self.api_client.response_data and self.last_group_loader.last_group is not None and self.to_insert:

            self.to_insert = False

            self.inserter.run(
                query=f"""
                INSERT INTO `hacker_news.top_stories` (story_id, created_at, group_id)
                VALUES {
                    ",".join([
                        str(val)
                        for val in tuple(
                            (
                                str(story_id),
                                dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                                self.last_group_loader.last_group
                            )
                            for story_id in self.api_client.response_data
                        )
                    ])}
                """,
                project=project,
                location=location,
                credentials=credentials,
            )

        if self.inserter.has_succeeded and self.api_client.has_succeeded:
            self.on_after_run()


    def on_after_run(self):
        self.should_execute = False
        self.to_insert = True
        self.last_group_loader.last_group += 1

