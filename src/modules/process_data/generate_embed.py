import json, datetime
from discord import Embed

from typing import *
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[3])


def structure_embed_alarm(
    structure: str,
    system: str,
    timestamp: str,
    thumbnail: str,
    health: str,
    attacking_char: str,
    attacking_corporation: str,
    attacking_alliance: str,
) -> Embed:
    with open(
        parent_dir_path + "/src/config/structure_under_attack_message.json", "r"
    ) as embed_file:
        embed_json = json.load(embed_file)

    embed_json["timestamp"] = timestamp
    embed_json["thumbnail"]["url"] = thumbnail
    embed_json["fields"][0]["value"] = structure
    embed_json["fields"][1]["value"] = system
    embed_json["fields"][2]["value"] = timestamp
    embed_json["fields"][3]["value"] = health
    embed_json["fields"][4]["value"] = attacking_char
    embed_json["fields"][5]["value"] = attacking_corporation
    embed_json["fields"][6]["value"] = attacking_alliance

    embed = Embed.from_dict(embed_json)

    return embed
