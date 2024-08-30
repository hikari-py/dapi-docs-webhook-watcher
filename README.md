# Discord API webhook poller for Discord

Polls GitHub to notify of any new commits to the API documentation, then sends it via a webhook to Discord.

## Running

Create a file called `.env` in the root of the repository and add:

```
DAPI_TRACKER_WEBHOOK_URL='<discord-webhook-url-here>'
```

Then run it using `docker compose up -d`.
