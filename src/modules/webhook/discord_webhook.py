from discord import Webhook, RequestsWebhookAdapter
import json

import sys
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[3])


class discordHook:
    def __init__(self) -> None:
        self.webhook_url = ""

    def sender(self, message: str, mention: str = "") -> None:
        webhook = Webhook.from_url(self.webhook_url, adapter=RequestsWebhookAdapter())
        webhook.send(embed=message)

    def set_webhook_url(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url
