import time
from threading import Thread

from hackernews_app.works.fastapi import FastAPIWork


def test_fastapi_work():
    api = FastAPIWork("fastapi_app", "app")
    thread = Thread(target=api.run, daemon=True)
    thread.start()
    time.sleep(2)
    assert api.health().status_code == 200
