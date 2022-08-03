from discord.ext.commands import Context

from database.db import get_currency
from modules import bot


@bot.command()
async def diggities(ctx: Context):
	key = ctx.author.id
	current_balance = get_currency(key)
	await ctx.author.send(f"You have **{current_balance} diggities**.")
