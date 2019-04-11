import os
from dotenv import load_dotenv
from bot import bot
import modules.dice


@bot.event
async def on_ready():
	print(f'Logged in as {bot.user.name} -- {bot.user.id}.')


@bot.event
async def on_message(message):
	if not message.author.bot:
		await bot.process_commands(message)


# Load env vars
load_dotenv()

bot_secret = os.getenv("BOT_TOKEN")
print(f"Using bot secret token: {bot_secret}")

bot.run(bot_secret)
