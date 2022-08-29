import sys
import argparse
from pathlib import Path

parent_dir_path = str(Path(__file__).resolve().parents[0])
sys.path.append(parent_dir_path + "/src/")

from squid_bot import *


def prepare_args(args=None) -> None:
    if args.config_path != None:
        config_path = args.config_path
    elif os.getenv("ConfigFilePath") != None:
        config_path = os.getenv("ConfigFilePath")
    else:
        raise

    with open(parent_dir_path + "/src/config/default.json", "r+") as f:
        config_data = json.load(f)
    with open(parent_dir_path + config_path, "r+") as f:
        config_site = json.load(f)

    run(
        http=config_site["server-info"]["seat-url"],
        token=config_site["server-info"]["seat-token"],
        http_eve=config_data["eve_api"]["https"],
        discord_webhook_url=config_site["webhook-url"],
        config_path=config_path,
    )


def main():
    parser = argparse.ArgumentParser(
        description="This program will get notification for SeAT server.",
        prog="SeAT server",
    )

    parser.add_argument(
        "--config-path",
        help="Destination of config file",
        type=str,
    )

    args = parser.parse_args()

    prepare_args(args)


if __name__ == "__main__":
    main()
