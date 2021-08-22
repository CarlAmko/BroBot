import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

bot_secret = os.getenv("BOT_TOKEN")
game_api_url = os.getenv("GAME_API_URL")
