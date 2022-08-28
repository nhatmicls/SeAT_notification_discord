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

loop_time = 120


class ProcessorActor(pykka.ThreadingActor):
    """
    Actor responsible for process data from device to server via protobuf.
    """

    def __init__(
        self,
        sink: pykka.ActorProxy,
        metric_submission_init_data: Dict[str, str] = None,
    ) -> None:
        super().__init__()
        self.sink = sink
        self.metric_submission_init_data = metric_submission_init_data

    def submit(
        self,
        data_recieve,
    ):

        pass


class Source(pykka.ThreadingActor):
    def __init__(
        self,
        process: pykka.ActorProxy,
        notification_ID: int,
        seat_api: API,
        eve_api: API,
        character_ID: int,
        producer: Callable[[int], Dict[str, str]],
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
            lambda _: process.submit(
                producer(
                    notification_ID=notification_ID,
                    seat_api=seat_api,
                    eve_api=eve_api,
                    character_ID=character_ID,
                )
            ),
        )

    def on_stop(self):
        self._disposable.dispose()


def producer(
    notification_ID: int,
    character_ID: int,
    seat_api: API,
    eve_api: API,
):
    def get_latest_notification(notification_ID, character_ID) -> None:
        target = str(character_ID)
        data = seat_api.get_api_data("seat_api", "character", "notifications", target)

    get_latest_notification(notification_ID, character_ID)


async def init() -> None:

    # Create temp folder if not exist
    dir = str(parent_dir_path) + "/queue_store"
    temp_dir = dir + "/temp"

    if not os.path.isdir(dir):
        os.mkdir(dir)
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    with open(dir + "/cache.dat", "r+") as f:
        cache_data = f.read()

    if cache_data is None:
        notification_ID = 0
    else:
        notification_ID = int(cache_data)

    process = ProcessorActor.start().proxy()
    source = Source.start(process=process, notification_ID=notification_ID).proxy()


def setup(api, hook, http, token, webhook_url) -> None:

    api.set_http(http)
    api.set_token(token)

    hook.set_webhook_url(webhook_url)

    return api, hook


def run() -> None:
    http = ""
    token = ""
    webhook_url = ""

    eve_api = API()
    seat_api = API()
    hook = discordHook()

    eve_api, hook = setup(eve_api, hook, http, token, webhook_url)
    data_process = processSeATApiData(eve_api, seat_api, 98549595)

    loop = asyncio.get_event_loop()
    loop.create_task(init())
    loop.run_forever()
