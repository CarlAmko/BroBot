import re

import emoji
from discord.ext.commands import Context

from modules import bot


@bot.command()
async def poll(ctx: Context):
	msg = ctx.message
	text = msg.content
	author = ctx.message.author

	choices = re.findall(r'"(.*?)"', text) or None
	if not choices:
		await ctx.send(f'No choices provided. Please use as **!poll "What are we playing?" "Choice 1" "Choice 2"**.')
		return

	question = choices[0]
	choices = choices[1:]

	num_poll_options = len(choices)
	if num_poll_options > 9:
		await ctx.send(f'Cannot provide more than 9 choices.')
		return

	def get_emoji(index: int) -> str:
		num_to_text = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
		return num_to_text[index]

	formatted_poll_options = '\n\t'.join([f':{get_emoji(i + 1)}: {v}' for i, v in enumerate(choices)])
	new_msg = await ctx.send(f'{author.mention} wants to know **{question}**\n\t{formatted_poll_options}')

	def get_emoji_as_unicode(index: int) -> str:
		output = emoji.emojize(f':keycap_{index}:')
		return output

	for i in range(num_poll_options):
		await new_msg.add_reaction(get_emoji_as_unicode(i + 1))
