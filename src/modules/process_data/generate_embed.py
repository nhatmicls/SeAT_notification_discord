import json, datetime
from discord import Embed

from typing import *
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[3])


def structure_embed_alarm(
    structure_name: str,
    system: str,
    timestamp: str,
    thumbnail: str,
    health: List[float],
    attacking_char: str,
    attacking_corporation: str,
    attacking_alliance: str,
) -> Embed:
    with open(
        parent_dir_path + "/src/database/structure_id.json", "r"
    ) as structure_id_file:
        structure_id_json = json.load(structure_id_file)
    with open(
        parent_dir_path + "/src/database/structure_thumbnail.json", "r"
    ) as structure_thumbnail_file:
        structure_thumbnail_json = json.load(structure_thumbnail_file)
    with open(
        parent_dir_path + "/src/config/structure_under_attack_message.json", "r"
    ) as embed_file:
        embed_json = json.load(embed_file)

    embed_json["timestamp"] = timestamp
    embed_json["thumbnail"]["url"] = structure_thumbnail_json[str(thumbnail)]
    embed_json["fields"][0]["value"] = structure_name
    embed_json["fields"][1]["value"] = system
    embed_json["fields"][2]["value"] = timestamp
    embed_json["fields"][3]["value"] = (
        "Shield percent: "
        + str(round(health[0], 3))
        + " Armor percent: "
        + str(round(health[1]))
        + " Hull percent: "
        + str(round(health[2]))
    )
    embed_json["fields"][4]["value"] = attacking_char
    embed_json["fields"][5]["value"] = attacking_corporation
    embed_json["fields"][6]["value"] = attacking_alliance

    embed = Embed.from_dict(embed_json)

    return embed
