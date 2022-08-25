import asyncio
from io import FileIO
import time
import persistqueue
import pykka
from rx.core.typing import Disposable
from rx.scheduler.eventloop import AsyncIOScheduler
from typing import *

import discord

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[1])
sys.path.append(parent_dir_path + "/src/modules/api")
sys.path.append(parent_dir_path + "/src/modules/webhook")

from seat_eve_api import API
from discord_webhook import discordHook

api = API()
hook = discordHook()


class task(pykka.ThreadingActor):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def get_latest_notification(self):
        pass

    def _push(self):
        def _next() -> None:
            pass


async def init():
    pass


def setup(http, token, webhook_url):
    global api, hook

    api.set_http(http)
    api.set_token(token)

    hook.set_webhook_url(webhook_url)


def run():
    http = ""
    token = ""
    webhook_url = ""

    setup(http, token, webhook_url)

    loop = asyncio.get_event_loop()
    loop.create_task(init())
    loop.run_forever()
