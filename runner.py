#!/usr/bin/env python3
# https://developer.github.com/v3/repos/commits/
# https://discordapp.com/developers/docs/resources/webhook#execute-webhook

import dataclasses
import datetime
import email.utils
import logging
import os
import sys
import time
import typing

import dacite
import dateutil.parser
import requests
import yaml


logging.basicConfig(level="INFO", format="%(asctime)23.23s %(levelname)1.1s %(message)s")


if len(sys.argv) != 3:
    logging.info("Please set a config file for the first argument, and a tracking file as the second")
    sys.exit(1)


@dataclasses.dataclass()
class Config:
    webhook_url: str
    period: float = 300
    threads: int = os.cpu_count() or 1
    api_url: str = "https://api.github.com/repos/discord/discord-api-docs/commits"
    params: typing.Dict[str, str] = dataclasses.field(default_factory=lambda: {"sha": "master"})


cfg_path, tracker_path = sys.argv[1:]

with open(tracker_path, "a+") as fp:
    last_update = fp.read().strip()

    if not last_update:
        last_update = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()


with open(cfg_path) as fp:
    config = dacite.from_dict(Config, yaml.safe_load(fp))


def poll() -> None:
    global last_update

    params = {**config.params, "since": last_update}

    with requests.get(config.api_url, params=params) as resp:
        resp.raise_for_status()
        data = resp.json()
        logging.info("GITHUB: %s %s", resp.status_code, resp.reason)

    last_update = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

    with open(tracker_path, "w") as fp:
        fp.write(last_update)

    if len(data) > 0:
        # new commits.
        data.sort(key=lambda ref: dateutil.parser.parse(ref["commit"]["committer"]["date"]))

        logging.info(f"Iterating across %s new commits", len(data))

        for commit in data:
            commit_detail = commit["commit"]
            committer = commit["committer"]
            author = commit["author"]

            logging.info("logging commit %s by %s via %s", commit_detail['tree']['sha'], author['login'], committer['login'])

            message = commit_detail["message"].strip() or "No message"

            webhook = {
                "username": f"By {committer['login'][:20]}",
                "avatar_url": committer["avatar_url"],
                "content": f"New Discord API documentation change: {commit['html_url']}",
                "embeds": [{
                    "author": {
                        "icon_url": author["avatar_url"],
                        "name": author["login"]
                    },
                    "title": "New commit",
                    "description": message[:2000] + ("..." if len(message) > 2000 else ""),
                    "timestamp": commit_detail["committer"]["date"],
                    "fields": [
                        {"name": "GPG", "value": commit_detail["verification"]["reason"].title(), "inline": True},
                        {"name": "When", "value": commit_detail["committer"]["date"], "inline": True},
                    ]
                }],
                "allowed_mentions": {
                    "parse": []
                }
            }

            while True:
                with requests.post(config.webhook_url, json=webhook) as resp:
                    if resp.status_code == 429:
                        date = email.utils.parsedate_to_datetime(resp.headers["Date"]).timestamp()
                        limit_end = float(resp.headers["X-RateLimit-Reset"])
                        sleep_for = max(0.0, limit_end - date)
                        logging.critical("Rate limited, so will wait for %ss", sleep_for)
                        time.sleep(sleep_for)
                        continue

                    resp.raise_for_status()
                    logging.info("DISCORD: %s %s", resp.status_code, resp.reason)
                    break
    else:
        logging.info("No new commits, going to sleep")


i = 0
while True:
    if i:
        time.sleep(config.period)

    try:
        poll()
    finally:
        i += 1
