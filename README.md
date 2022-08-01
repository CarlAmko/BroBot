# BroBot
Discord bot with a variety of commands.

# Setup
The BroBot stack runs in containers to allow for maximum platform compatibility.

## Windows
Get [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/), which should include everything you need.

## Linux
Either:
1. Install [Docker Engine](https://docs.docker.com/engine/install/) and the [Docker Compose plugin](https://docs.docker.com/compose/install/), or
2. Get [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/).

# Environment
Environment variables are passed into Docker containers via a `.env` file. 

You will need to create one and add the appropriate values as follows:
```dotenv
# Auth token for running the bot. BroBot will not function without this.
BOT_TOKEN=$BOT_TOKEN
# The ID server the bot is running on. Multi-server is currently not supported.
GUILD_ID=$GUILD_ID
# (Optional) The ID of a channel that tracks member count.
MEMBER_CHANNEL_ID=$MEMBER_CHANNEL_ID
# (Optional) If you wish to use the Reddit API, the CLIENT_ID and CLIENT_SECRET for your account. 
REDDIT_API_CLIENT_ID=$REDDIT_API_CLIENT_ID
REDDIT_API_CLIENT_SECRET=$REDDIT_API_CLIENT_SECRET
# (Optional) GamePrices API endpoint.
GAME_API_ENDPOINT=$GAME_API_ENDPOINT
# Redis database endpoint. Defaults to pointing to the redis container running via Docker compose.
REDIS_ENDPOINT=redis
```

# Running
## Starting
`docker compose up --build -d`

## Restarting after making local changes
`docker compose up --build brobot`

## Checking logs
`docker compose logs -f brobot`