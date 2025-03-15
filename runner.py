# Copyright (c) 2025-present davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://developer.github.com/v3/repos/commits/
# https://discordapp.com/developers/docs/resources/webhook#execute-webhook
from __future__ import annotations

import datetime
import email.utils
import http
import json
import logging
import pathlib
import time
import typing

import click
import dateutil.parser
import dotenv
import requests

if typing.TYPE_CHECKING:

    class PartialActionUser(typing.TypedDict):
        name: str
        email: str
        date: str

    class ActionUser(PartialActionUser):
        avatar_url: str
        login: str

    class Tree(typing.TypedDict):
        url: str
        sha: str

    class Verification(typing.TypedDict):
        verified: bool
        reason: str
        signature: str | None
        payload: str | None

    class CommitDetail(typing.TypedDict):
        author: PartialActionUser
        committer: PartialActionUser
        message: str
        tree: Tree
        verification: Verification

    class Commit(typing.TypedDict):
        author: ActionUser
        commit: CommitDetail
        committer: ActionUser
        html_url: str


def _now() -> str:
    return datetime.datetime.now(tz=datetime.UTC).isoformat()


_MAX_DESCRIPTION_LEN = 2000
_LOGGER = logging.getLogger("watcher")


def _poll(webhook_url: str, tracker_path: pathlib.Path, api_url: str, params: dict[str, str], last_update: str) -> str:
    params = {**params, "since": last_update}

    with requests.get(api_url, params=params, headers={"X-GitHub-Api-Version": "2022-11-28"}) as resp:
        resp.raise_for_status()
        data = typing.cast("list[Commit]", resp.json())
        _LOGGER.info("GITHUB: %s %s", resp.status_code, resp.reason)

    last_update = _now()
    tracker_path.write_text(last_update)

    # new commits.
    data.sort(key=lambda ref: dateutil.parser.parse(ref["commit"]["committer"]["date"]))
    _LOGGER.info("Iterating across %s new commits", len(data))

    for commit in data:
        commit_detail = commit["commit"]
        committer = commit["committer"]
        author = commit["author"]

        _LOGGER.info(
            "logging commit %s by %s via %s", commit_detail["tree"]["sha"], author["login"], committer["login"]
        )

        message = commit_detail["message"].strip() or "No message"
        if len(message) > _MAX_DESCRIPTION_LEN:
            message = f"{message[:_MAX_DESCRIPTION_LEN]}..."

        webhook = {
            "username": f"By {committer['login'][:20]}",
            "avatar_url": committer["avatar_url"],
            "content": f"New Discord API documentation change: {commit['html_url']}",
            "embeds": [
                {
                    "author": {"icon_url": author["avatar_url"], "name": author["login"]},
                    "title": "New commit",
                    "description": message,
                    "timestamp": commit_detail["committer"]["date"],
                    "fields": [
                        {"name": "GPG", "value": commit_detail["verification"]["reason"].title(), "inline": True},
                        {"name": "When", "value": commit_detail["committer"]["date"], "inline": True},
                    ],
                }
            ],
            "allowed_mentions": {"parse": list[int]()},
        }

        while True:
            with requests.post(webhook_url, json=webhook) as resp:
                if resp.status_code == http.HTTPStatus.TOO_MANY_REQUESTS:
                    date = email.utils.parsedate_to_datetime(resp.headers["Date"]).timestamp()
                    limit_end = float(resp.headers["X-RateLimit-Reset"])
                    sleep_for = max(0.0, limit_end - date)
                    _LOGGER.critical("Rate limited, so will wait for %ss", sleep_for)
                    time.sleep(sleep_for)
                    continue

                resp.raise_for_status()
                _LOGGER.info("DISCORD: %s %s", resp.status_code, resp.reason)
                break

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
    "--api-url", envvar="DAPI_TRACKER_API_URL", default="https://api.github.com/repos/discord/discord-api-docs/commits"
)
@click.option(
    "--params", envvar="DAPI_TRACKER_PARAMS_PATH", type=click.Path(exists=True, path_type=pathlib.Path), default=None
)
def main(webhook_url: str, tracker_path: pathlib.Path, period: int, api_url: str, params: pathlib.Path | None) -> None:
    logging.basicConfig(level="INFO", format="%(asctime)23.23s %(levelname)1.1s %(message)s")

    if params:
        with params.open("r") as file:
            params_dict: dict[str, str] = json.load(file)

    else:
        params_dict = {"sha": "main"}

    last_update = tracker_path.read_text().strip() if tracker_path.exists() else _now()

    while True:
        try:
            last_update = _poll(
                webhook_url=webhook_url,
                tracker_path=tracker_path,
                api_url=api_url,
                params=params_dict,
                last_update=last_update,
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            requests.exceptions.JSONDecodeError,
            requests.exceptions.InvalidJSONError,
        ) as ex:
            _LOGGER.exception("Failed to fetch latest update, backing off and trying again later", exc_info=ex)

        time.sleep(period)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
