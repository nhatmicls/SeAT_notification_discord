import asyncio
from io import FileIO
import time

import discord

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[1])
sys.path.append(parent_dir_path + "/src/modules/notification")
sys.path.append(parent_dir_path + "/src/modules/webhook")

from seat_api import *


def setup():
    pass


def run():
    loop = asyncio.get_event_loop()
