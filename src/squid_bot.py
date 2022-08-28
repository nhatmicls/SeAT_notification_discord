import asyncio
from io import FileIO
import time
import persistqueue
import pykka
from rx.core.typing import Disposable
from rx.scheduler.eventloop import AsyncIOScheduler
from asyncio.events import AbstractEventLoop
from asyncio.futures import Future
from typing import *
import os
import json

import discord
from datetime import datetime

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[1])
sys.path.append(parent_dir_path + "/src/modules/api")
sys.path.append(parent_dir_path + "/src/modules/webhook")

from seat_eve_api import API
from discord_webhook import discordHook
from bot_queue import clientQueue
from bot_task import botTask
from process_data import processSeATApiData
from FileIO import *

loop_time = 5


class Source(pykka.ThreadingActor):
    def __init__(
        self,
        character_ID: int,
        producer: botTask,
    ):
        """
        @param process   the ActorProxy of the actor responsible for sending data
        @param producer  function responsible for producing data.
                         For example, in the case of modbus, this is where modbus
                         read can be performed.
        """
        super().__init__()
        scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self._disposable = scheduler.schedule_periodic(
            loop_time,
            lambda _: producer.producer(character_ID=character_ID),
        )

    def on_stop(self):
        self._disposable.dispose()


async def init(
    eve_api: API,
    seat_api: API,
    discord_webhook: discordHook,
    config_path: str = "/config/config.json",
) -> None:
    # Create temp folder if not exist
    dir = str(parent_dir_path) + "/queue_store"

    if not os.path.isdir(dir):
        os.mkdir(dir)

    try:
        cache_data = json2dict(dir + "/cache.json")
    except:
        json_init = {"last_notification_ID": 0, "current_notification_page": 1}
        dict2json(dir + "/cache.json", json_init)
        cache_data = json2dict(dir + "/cache.json")

    with open(parent_dir_path + config_path, "r+") as f:
        config_data = json.load(f)

    if cache_data is None:
        notification_ID = 0
    else:
        notification_ID = int(cache_data["last_notification_ID"])
        current_notification_page = int(cache_data["current_notification_page"])

    character_ID = config_data["ceo-member"]

    producer = botTask(
        last_notification_ID=notification_ID,
        current_notification_page=current_notification_page,
        seat_api=seat_api,
        eve_api=eve_api,
        discord_webhook=discord_webhook,
        mention=config_data["mention-list"],
    )
    source = Source.start(producer=producer, character_ID=character_ID).proxy()


def run(
    http: str,
    token: str,
    http_eve: str,
    discord_webhook_url: str,
    config_path: str = "/config/config.json",
) -> None:

    eve_api = API()
    seat_api = API()
    discord_webhook = discordHook()

    seat_api.set_http(http)
    seat_api.set_token(token)

    eve_api.set_http(http_eve)

    discord_webhook.set_webhook_url(discord_webhook_url)

    loop = asyncio.get_event_loop()
    loop.create_task(
        init(
            eve_api=eve_api,
            seat_api=seat_api,
            discord_webhook=discord_webhook,
            config_path=config_path,
        )
    )
    loop.run_forever()
