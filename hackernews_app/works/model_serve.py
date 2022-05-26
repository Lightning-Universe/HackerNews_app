import subprocess
import time
import random

import requests
from lightning import LightningWork

class FastAPIWork(LightningWork):
    def __init__(self, module, api_object):
        super().__init__(run_once=True)
        self.module = module
        self.api_object = api_object
        self.is_running = False
        self._process = None
        self.url = self._future_url

    def run(self, kill=False):
        if kill:
            self._process.terminate()

        if self._process is None:
            command = [
                "uvicorn",
                f"{self.module}:{self.api_object}",
                "--port",
                str(self.port),
                "--host",
                self.host
            ]
            self._process = subprocess.Popen(command).wait()

            time.sleep(5)

        if self.url is None:
            return

        self.url = self._url

        resp = requests.get(f"{self._url}/healthz")
        if resp.status_code == 200:
            self.is_running = True