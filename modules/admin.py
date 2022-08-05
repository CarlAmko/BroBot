from discord.ext.commands import Context

from modules import bot
from env import ADMIN_IDS


@bot.command()
async def purge(ctx: Context):
	author = ctx.author
	if author.id in ADMIN_IDS:
		# only 100 messages
		await ctx.channel.purge()
		await ctx.send(f'{author.mention} Purge successful.')
	else:
		await ctx.send(f'{author.mention} You do not have permission to do that.')


@bot.command()
async def purgeall():
	pass
