import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

bot_secret = os.getenv("BOT_TOKEN")
game_api_url = os.getenv("GAME_API_URL")
guild_id = os.getenv("GUILD_ID")
member_channel_id = os.getenv("MEMBER_CHANNEL_ID")

reddit_client_id = os.getenv("REDDIT_API_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_API_CLIENT_SECRET")
reddit_user = os.getenv("REDDIT_USER")
reddit_pass = os.getenv("REDDIT_PASS")
