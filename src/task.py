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


def get_notification():
    pass


def get_latest_notification():
    pass


def get_structure_name(seat_api: API):
    return seat_api.get_api_data("seat_api", "corporation", "structures", "98549595")
