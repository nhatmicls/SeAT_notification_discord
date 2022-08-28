from io import FileIO
import time

import discord

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[1])
sys.path.append(parent_dir_path + "/src/modules/api")
sys.path.append(parent_dir_path + "/src/modules/process_data")
sys.path.append(parent_dir_path + "/src/modules/webhook")

from seat_eve_api import API
from process_data import processSeATApiData


class botTask:
    def __init__(self, notification_ID) -> None:
        super().__init__()

    def _push(self):
        def _entry_point() -> None:
            pass

        def get_notification() -> None:
            pass

        def get_latest_notification() -> None:
            pass

        def get_structure_name() -> None:
            pass
