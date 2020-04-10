# Discord API webhook poller for Discord

Polls GitHub to notify of any new commits to the API documentation, then sends it via a webhook to Discord.

## Config

Make a directory called `data`. Place this inside:

`config.yaml`
```yaml
webhook_url: http://discord-webhook-url-here
```

## Running

Run `docker-compose up -d`.
