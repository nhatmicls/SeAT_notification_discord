import requests
import json

from typing import *

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[3])


class WebAPI:
    def __init__(self) -> None:
        self.http = ""
        self.token = ""

        with open(parent_dir_path + "\src\config\default.json", "r") as f:
            self.json_file = json.load(f)

    def _api_check(func):
        def inner(self, *args, **kwargs):
            if self.http != "" and self.token != "":
                return func(self, *args, **kwargs)
            else:
                print("Missing data")
                raise ValueError

        return inner

    @_api_check
    def get_api_data(
        self, hierarchi: str, type: str, target: str = ""
    ) -> requests.models.Response:
        data = self.json_file["mapping_api"][hierarchi][type]
        data += target

        return self._get_api_data(data)

    @_api_check
    def _get_api_data(self, api: str) -> requests.models.Response:
        http_request = self.http + api
        return requests.get(
            http_request,
            headers={
                "accept": "application/json",
                "X-Token": self.token,
                "X-CSRF-TOKEN": "",
            },
        )

    def set_http(self, http: str) -> None:
        self.http = http

    def set_token(self, token: str) -> None:
        self.token = token
