#!/usr/bin/env python3
# https://developer.github.com/v3/repos/commits/
# https://discordapp.com/developers/docs/resources/webhook#execute-webhook

import dataclasses
import datetime
import email.utils
import json
import logging
import pathlib
import time
import typing

import click
import dateutil.parser
import dotenv
import requests


def _now() -> str:
    return datetime.datetime.now(tz=datetime.timezone.utc).isoformat()


def _poll(
    webhook_url: str,
    tracker_path: pathlib.Path,
    api_url: str,
    params: dict[str, str],
    last_update: str,
) -> str:
    params = {**params, "since": last_update}

    with requests.get(api_url, params=params) as resp:
        resp.raise_for_status()
        data = resp.json()
        logging.info("GITHUB: %s %s", resp.status_code, resp.reason)

    last_update = _now()
    tracker_path.write_text(last_update)

    if len(data) > 0:
        # new commits.
        data.sort(key=lambda ref: dateutil.parser.parse(ref["commit"]["committer"]["date"]))

        logging.info(f"Iterating across %s new commits", len(data))

        for commit in data:
            commit_detail = commit["commit"]
            committer = commit["committer"]
            author = commit["author"]

            logging.info(
                "logging commit %s by %s via %s", commit_detail['tree']['sha'], author['login'], committer['login']
            )

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
                with requests.post(webhook_url, json=webhook) as resp:
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

    return last_update


@click.command()
@click.argument("webhook_url", envvar="DAPI_TRACKER_WEBHOOK_URL")
@click.option(
    "--tracker-path",
    default="./dapi_tracker_updated",
    envvar="DAPI_TRACKER_PATH",
    type=click.Path(exists=False, path_type=pathlib.Path),
)
@click.option("--period", envvar="DAPI_TRACKER_PERIOD", type=int, default=300)
@click.option(
    "--api-url",
    envvar="DAPI_TRACKER_API_URL",
    default="https://api.github.com/repos/discord/discord-api-docs/commits",
)
@click.option(
    "--params",
    envvar="DAPI_TRACKER_PARAMS",
    type=click.Path(exists=True, path_type=pathlib.Path),
    default=None,
)
def main(
    webhook_url: str,
    tracker_path: pathlib.Path,
    period: int,
    api_url: str,
    params: pathlib.Path | None,
):
    logging.basicConfig(level="INFO", format="%(asctime)23.23s %(levelname)1.1s %(message)s")

    if params:
        with params.open("r") as file:
            params_dict: dict[str, str] = json.load(file)

    else:
        params_dict = {"sha": "main"}

    if tracker_path.exists():
        last_update = tracker_path.read_text().strip() or _now()
    else:
        last_update = _now()

    while True:
        last_update = _poll(
            webhook_url=webhook_url,
            tracker_path=tracker_path,
            api_url=api_url,
            params=params_dict,
            last_update=last_update, 
        )
        time.sleep(period)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
