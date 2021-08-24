from random import choice
import re

from modules import bot


@bot.command()
async def random(ctx):
	msg = ctx.message
	text = msg.content
	author = ctx.message.author

	matches = re.findall(r'"(.*?)"', text) or None
	if not matches:
		await ctx.send(f'No choices provided. Please use as **!random "Choice 1" "Choice 2" "Choice 3"**.')
		return

	picked = choice(matches)
	await ctx.send(f'{author.mention} I have selected... **{picked}**!')
