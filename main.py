import env
from bot import bot
import modules.dice
import modules.game_price


@bot.event
async def on_ready():
	print(f'Logged in as {bot.user.name} -- {bot.user.id}.')


@bot.event
async def on_message(message):
	if not message.author.bot:
		await bot.process_commands(message)


print(f"Using bot secret token: {env.bot_secret}")
bot.run(env.bot_secret)
