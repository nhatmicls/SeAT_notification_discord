import generate_embed
from discord import Embed

import json, requests

from typing import *
from pathlib import Path
import sys

parent_dir_path = str(Path(__file__).resolve().parents[3])
sys.path.append(parent_dir_path + "/src/modules/api")

from seat_eve_api import API


class processSeATApiData:
    def __init__(self, eve_api: API, seat_api: API) -> None:
        self.eve_api = eve_api
        self.seat_api = seat_api

    def preprocess_api_data(self, api_data_input: requests.Response) -> Dict[str, Any]:
        data = (api_data_input.content).decode("utf-8")
        return json.loads(data)

    def process_structure_name(
        self, api_data_input: requests.Response, structureID: str
    ) -> str:
        preprocess_data = self.preprocess_api_data(api_data_input)

        for x in preprocess_data["data"]:
            if x["structure_id"] == structureID:
                return x["info"]["name"]

    def process_system_name(self, api_data_input: requests.Response) -> str:
        preprocess_data = self.preprocess_api_data(api_data_input)
        return preprocess_data["name"]

    def process_object_name(self, api_data_input: requests.Response) -> str:
        preprocess_data = self.preprocess_api_data(api_data_input)
        return preprocess_data["name"]

    def process_character_info(
        self, api_data_input: requests.Response, return_id_type: bool = False
    ) -> Dict[str, str]:
        preprocess_data = self.preprocess_api_data(api_data_input)
        corp_info = self.preprocess_api_data(
            self.eve_api.get_api_data(
                "eve_api",
                "corporations",
                "corporations",
                str(preprocess_data["corporation_id"]),
            )
        )
        try:
            alliance_info = self.preprocess_api_data(
                self.eve_api.get_api_data(
                    "eve_api",
                    "alliances",
                    "alliances",
                    str(preprocess_data["alliance_id"]),
                )
            )
        except:
            alliance_info = ""

        if return_id_type == True:
            try:
                alliance_id = preprocess_data["alliance_id"]
            except:
                alliance_id = 0
            character_info = {
                "character_name": preprocess_data["name"],
                "corp_name": preprocess_data["corporation_id"],
                "alliance_name": alliance_id,
            }
        else:
            character_info = {
                "character_name": preprocess_data["name"],
                "corp_name": corp_info["name"],
                "alliance_name": alliance_info["name"],
            }
        return character_info

    def process_structure_have_been_shoot(
        self, api_data_input: requests.Response, character_id_notification: int
    ):
        preprocess_data = self.preprocess_api_data(api_data_input)

        for data in preprocess_data["data"]:
            if data["type"] == "StructureUnderAttack":
                character_api = self.eve_api.get_api_data(
                    "eve_api",
                    "characters",
                    "characters",
                    str(character_id_notification),
                )
                character_info = self.process_character_info(
                    character_api, return_id_type=True
                )

                structure_api = self.seat_api.get_api_data(
                    "seat_api",
                    "corporation",
                    "structures",
                    str(character_info["corp_name"]),
                )
                structure_name = self.process_structure_name(
                    structure_api, int(data["text"]["structureID"])
                )

                system_api = self.eve_api.get_api_data(
                    "eve_api", "universe", "systems", str(data["text"]["solarsystemID"])
                )
                system_name = self.process_system_name(system_api)

                character_attack_api = self.eve_api.get_api_data(
                    "eve_api",
                    "characters",
                    "characters",
                    str(data["text"]["charID"]),
                )
                character_attack_info = self.process_character_info(
                    character_attack_api
                )

                return generate_embed.structure_embed_alarm(
                    structure_name=structure_name,
                    system=system_name,
                    timestamp=data["timestamp"],
                    thumbnail=data["text"]["structureTypeID"],
                    health=(
                        data["text"]["shieldPercentage"],
                        data["text"]["armorPercentage"],
                        data["text"]["hullPercentage"],
                    ),
                    attacking_char=character_attack_info["character_name"],
                    attacking_alliance=character_attack_info["alliance_name"],
                    attacking_corporation=character_attack_info["corp_name"],
                )
