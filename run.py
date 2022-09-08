import os
import json

import discord
from datetime import datetime

import sys
import argparse
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[0])
sys.path.append(parent_dir_path + "/src")

from squid_bot import run

run()
