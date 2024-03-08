# Discord API webhook poller for Discord

Polls GitHub to notify of any new commits to the API documentation, then sends it via a webhook to Discord.

## Running

Run `docker-compose up -d -e 'DAPI_TRACKER_PATH'='http://discord-webhook-url-here'`.
