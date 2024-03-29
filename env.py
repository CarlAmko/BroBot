import json
import os

# import dotenv

# dotenv.load_dotenv()

BOT_SECRET = os.getenv("BOT_TOKEN")
GAME_API_URL = os.getenv("GAME_API_URL")
GUILD_ID = os.getenv("GUILD_ID")

REDDIT_CLIENT_ID = os.getenv("REDDIT_API_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_API_CLIENT_SECRET")
REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")

MEMBER_CHANNEL_ID = int(os.getenv("MEMBER_CHANNEL_ID")) if "MEMBER_CHANNEL_ID" in os.environ else None
ADMIN_IDS = json.loads(os.getenv("ADMIN_IDS")) if "ADMIN_IDS" in os.environ else None

BETA = os.getenv("BETA") == "True" if "BETA" in os.environ else False
