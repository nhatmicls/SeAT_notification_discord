import generate_embed

import json, requests

from typing import *
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[3])


def process_data(api_data_input: requests.Response):
    preprocess_data = preprocess_api_data(api_data_input)
    process_structure_have_been_shoot(preprocess_data)


def preprocess_api_data(api_data_input: requests.Response) -> Dict[str, Any]:
    data = (api_data_input.content).decode("utf-8")
    return json.loads(data)


def process_structure_have_been_shoot(data_input: Dict[str, Any]):
    for data in data_input["data"]:
        if data["type"] == "StructureUnderAttack":
            data_send = generate_embed.structure_embed_alarm(
                structure=data["structureID"],
                system=data["solarsystemID"],
                timestamp=data["timestamp"],
                thumbnail=data["structureTypeID"],
                health=(
                    data["shieldPercentage"],
                    data["armorPercentage"],
                    data["hullPercentage"],
                ),
                attacking_char=data["charID"],
                attacking_alliance=data["allianceName"],
                attacking_corporation=data["corpName"],
            )
