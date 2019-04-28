import json

import requests
import env
from bot import bot


@bot.command()
async def price(ctx):
	msg = ctx.message
	text = msg.content

	# split off command from message
	splits = text.split(" ", 1)

	# check for valid input
	if not splits or len(splits) < 2:
		await ctx.send(f'{msg.author.mention} Invalid input. Example: !price *GAME*.')

	# extract query from list
	query = splits[1]
	print(f"Querying '{query}'...")

	# send request to API
	resp = requests.get(url=f'{env.game_api_url}steam/{query}').json()
	print(f'Got response: {resp}')

	# Check if response found a game for query
	if 'No result found' in resp:
		await ctx.send(f'{msg.author.mention} No game found for search term: \'{query}\'')
	else:
		data = json.loads(resp)
		# format and reply response
		await ctx.send(f'{msg.author.mention} Found game on Steam:\n*{data["name"]}* @ **${data["price"] / 100}**')
