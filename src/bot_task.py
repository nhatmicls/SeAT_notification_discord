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


class botTask:
    def __init__(
        self,
        last_notification_ID: int,
        seat_api: API,
        eve_api: API,
        discord_webhook: discordHook,
        mention: Dict[str, str],
    ) -> None:
        super().__init__()
        self.last_notification_ID = last_notification_ID
        self.seat_api = seat_api
        self.processData = processSeATApiData(eve_api, seat_api)
        self.current_notification_page = 1
        self.discord_webhook_url = discord_webhook
        self.mention = mention

    def get_oldest_notification(self, character_ID) -> requests.Response:
        target = str(character_ID)
        data = self.seat_api.get_api_data(
            "seat_api", "character", "notifications", target
        )
        return data

    def get_next_notification(self, character_ID) -> requests.Response:
        if self.current_notification_page == 1:
            target = str(character_ID)
        else:
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

    def producer(self, character_ID):

        try:
            data = self.get_next_notification(character_ID=character_ID)
        except:
            if self.current_notification_page == 1 and self.last_notification_ID == 0:
                data = self.get_oldest_notification(character_ID=character_ID)
                self.set_current_notification_page(data)
                data = self.get_next_notification(character_ID=character_ID)

        if data is not None:
            self.set_last_notification_id(data)
            self.set_next_notification_page(data)

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
