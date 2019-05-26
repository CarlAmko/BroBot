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
	resp = json.loads(requests.get(url=f'{env.game_api_url}{query}').json())
	print(f'Got response: {resp}')

	# Check if response found a game for query
	if not resp["results"]:
		await ctx.send(f'{msg.author.mention} No game found for search term: \'{query}\'')
	else:
		data = resp["results"]
		# format and reply response
		await ctx.send(f'{msg.author.mention} Found game...\n')
		for res in data:
			res = json.loads(res)
			print(f'Parsing result: {res}')
			await ctx.send(f'{res["name"]} for **${res["price"] / 100}** on *{res["provider"].capitalize()}*')
