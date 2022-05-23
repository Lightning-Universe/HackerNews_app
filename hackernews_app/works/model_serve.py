import subprocess
import time
import random

import requests
from lightning import LightningWork

class FastAPIWork(LightningWork):
    def __init__(self, module, api_object, host="localhost", port=8000):
        super().__init__(run_once=True)
        self.module = module
        self.api_object = api_object
        self._host = host
        self._port = port
        self.is_running = False
        self._process = None
        self.base_url = f"http://{self._host}:{self._port}"

    def run(self, kill=False):
        if kill:
            self._process.terminate()

        if self._process is None:
            command = [
                "uvicorn",
                f"{self.module}:{self.api_object}",
                "--port",
                str(self._port),
            ]
            self._process = subprocess.Popen(command)
            time.sleep(5)

        resp = requests.get(f"{self.base_url}/healthz")
        if resp.status_code == 200:
            self.is_running = True