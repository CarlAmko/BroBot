import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

BOT_SECRET = os.getenv("BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL")
GUILD_ID = os.getenv("GUILD_ID")
MEMBER_CHANNEL_ID = os.getenv("MEMBER_CHANNEL_ID")

REDDIT_CLIENT_ID = os.getenv("REDDIT_API_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_API_CLIENT_SECRET")
REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")

WORDLE_CHANNEL_ID = os.getenv("WORDLE_CHANNEL_ID")
