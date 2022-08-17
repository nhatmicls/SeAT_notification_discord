import requests
import json
from typing import *

res = requests.get(
    "http://squidinc.space/api/v2/character/notifications/2115472521?page=335",
    headers={
        "accept": "application/json",
        "X-Token": "dlAipmOYMLJnJNGY9TblfoEAPefg4ffQ",
        "X-CSRF-TOKEN": "",
    },
)

data = (res.content).decode("utf-8")
json_data: Dict[str, Any] = json.loads(data)

for x in json_data["data"]:
    # print(x)
    if x["type"] == "StructureUnderAttack":
        print(x)

# print(res)
# print(res.headers)
# print(json_data["data"])
