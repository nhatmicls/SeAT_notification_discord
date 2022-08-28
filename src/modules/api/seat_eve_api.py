import requests
import json

from typing import *

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[3])


class API:
    def __init__(self) -> None:
        self.http = ""
        self.token = ""
        self.data_source = ""

        with open(parent_dir_path + "/src/config/default.json", "r") as f:
            self.json_file = json.load(f)

    def _http_check(func):
        def inner(self, *args, **kwargs):
            if self.http != "":
                return func(self, *args, **kwargs)
            else:
                print("Missing request https")
                raise ValueError

        return inner

    @_http_check
    def get_api_data(
        self, type_api: str, hierarchi: str, type: str, target: str = ""
    ) -> requests.models.Response:
        data: str = self.json_file[type_api][hierarchi][type]
        data = data.replace("{id}", str(target))

        return self._get_api_data(type_api, data)

    @_http_check
    def _get_api_data(self, type_api: str, api: str) -> requests.models.Response:
        http_request = self.http + api

        # Start get data
        if type_api == "seat_api":
            return requests.get(
                http_request,
                headers={
                    "accept": "application/json",
                    "X-Token": self.token,
                    "X-CSRF-TOKEN": "",
                },
            )
        elif type_api == "eve_api":
            http_request += self.data_source
            return requests.get(
                http_request,
                headers={
                    "accept": "application/json",
                    "Cache-Control": "no-cache",
                },
            )
        else:
            return None

    def set_http(self, http: str) -> None:
        self.http = http

    def set_token(self, token: str) -> None:
        self.token = token

    def set_data_source(self, data_source: str) -> None:
        self.data_source = data_source
