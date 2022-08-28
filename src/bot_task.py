from io import FileIO
import time
import requests

import discord

import sys
from pathlib import Path
from typing import *

parent_dir_path = str(Path(__file__).resolve().parents[1])
sys.path.append(parent_dir_path + "/src/modules/api")
sys.path.append(parent_dir_path + "/src/modules/process_data")
sys.path.append(parent_dir_path + "/src/modules/webhook")

from seat_eve_api import API
from process_data import processSeATApiData
from discord_webhook import discordHook
from FileIO import *


class botTask:
    def __init__(
        self,
        seat_api: API,
        eve_api: API,
        discord_webhook: discordHook,
        mention: Dict[str, str],
        last_notification_ID: int = 0,
        current_notification_page: int = 1,
    ) -> None:
        super().__init__()
        self.last_notification_ID = last_notification_ID
        self.seat_api = seat_api
        self.processData = processSeATApiData(eve_api, seat_api)
        self.current_notification_page = current_notification_page
        self.discord_webhook_url = discord_webhook
        self.mention = mention

        if self.current_notification_page < 1:
            self.current_notification_page = 1

    def get_oldest_notification(self, character_ID) -> requests.Response:
        target = str(character_ID)
        data = self.seat_api.get_api_data(
            "seat_api", "character", "notifications", target
        )
        return data

    def get_last_notification_page(self, character_ID) -> int:
        target = str(character_ID) + "?page=1"
        data = self.seat_api.get_api_data(
            "seat_api", "character", "notifications", target
        )
        preprocess_data = self.processData.preprocess_api_data(data)
        return preprocess_data["meta"]["last_page"]

    def get_next_notification(self, character_ID) -> requests.Response:
        target = str(character_ID) + "?page=" + str(self.current_notification_page)
        data = self.seat_api.get_api_data(
            "seat_api", "character", "notifications", target
        )

        preprocess_data = self.processData.preprocess_api_data(data)
        if (
            self.last_notification_ID
            == preprocess_data["data"][len(preprocess_data["data"]) - 1][
                "notification_id"
            ]
        ):
            if (
                self.get_last_notification_page(character_ID=character_ID)
                == self.current_notification_page
            ):
                return

        return data

    def set_current_notification_page(self, api_data_input: requests.Response) -> None:
        preprocess_data = self.processData.preprocess_api_data(api_data_input)
        self.current_notification_page = preprocess_data["meta"]["current_page"]

    def set_next_notification_page(self, api_data_input: requests.Response) -> None:
        preprocess_data = self.processData.preprocess_api_data(api_data_input)
        if len(preprocess_data["data"]) == 15:
            self.current_notification_page += 1

    def set_last_notification_id(self, api_data_input: requests.Response) -> None:
        preprocess_data = self.processData.preprocess_api_data(api_data_input)
        self.last_notification_ID = preprocess_data["data"][
            len(preprocess_data["data"]) - 1
        ]["notification_id"]

    def save_cache(self):
        json_init = {
            "last_notification_ID": self.last_notification_ID,
            "current_notification_page": self.current_notification_page,
        }
        dict2json(parent_dir_path + "/queue_store/cache.json", json_init)

    def producer(self, character_ID):
        data = None
        try:
            data = self.get_next_notification(character_ID=character_ID)
            fix_data = self.get_last_notification_page(character_ID=character_ID)
            if self.current_notification_page > fix_data:
                raise
        except:
            fix_data = self.get_last_notification_page(character_ID=character_ID)
            if self.current_notification_page < fix_data + 1:
                data = self.get_oldest_notification(character_ID=character_ID)
                self.set_current_notification_page(data)
                data = self.get_next_notification(character_ID=character_ID)

        if data is not None:
            self.set_last_notification_id(data)
            self.set_next_notification_page(data)
            self.save_cache()

            data_send = self.processData.process_structure_have_been_shoot(
                api_data_input=data, character_id_notification=int(character_ID)
            )
            if data_send is not None:
                self.discord_webhook_url.sender(
                    data_send, mention=self.mention["StructureUnderAttack"]
                )

    def first_run(self, character_ID):
        if self.current_notification_page == 0:
            self.get_oldest_notification(character_ID=character_ID)
            self.set_current_notification_page(character_ID=character_ID)
        else:
            self.get_next_notification(character_ID=character_ID)
