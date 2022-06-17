import requests
from discord.ext.commands import Context

import env
from modules import bot


@bot.command()
async def price(ctx: Context):
	msg = ctx.message
	text = msg.content

	# split off command from message
	request = text.split(" ", 1)

	# check for valid input
	if not request or len(request) < 2:
		await ctx.send(f'{msg.author.mention} Invalid input. Example: !price <GAME>.')

	# extract query from list
	query = request[1]
	print(f"Querying '{query}'...")

	# send request to API
	params = {'query': query}
	resp_json = requests.get(url=f'{env.game_api_url}', params=params).json()
	print(f'Got response: {resp_json}')

	num_results = len(resp_json)
	if resp_json and num_results > 1:
		human_readable_names = {
			'hb': 'Humble Bundle',
			'steam': 'Steam',
			'g2a': 'G2A'
		}

		lines = []
		for resp in resp_json:
			provider = human_readable_names[resp['provider']]
			lines.append(f'{resp["name"]} on **{provider}** for **${resp["price"]}**.')

		line_str = "\n\t".join(lines)
		await ctx.send(f'{msg.author.mention}, found {num_results} results for \'{query}\':\n\t{line_str}')
	else:
		await ctx.send(f'{msg.author.mention} No game found for search term: \'{query}\'')
