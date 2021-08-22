#!/usr/bin/env python3

import env
from modules import bot
from modules import dice, game_price

@bot.event
async def on_ready():
	print(f'Logged in as {bot.user.name} -- {bot.user.id}.')


@bot.event
async def on_message(message):
	if not message.author.bot:
		await bot.process_commands(message)


if __name__ == '__main__':
	print(f"Using bot secret token: {env.bot_secret}")
	bot.run(env.bot_secret)
