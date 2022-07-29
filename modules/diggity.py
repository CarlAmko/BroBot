import emoji
from discord import Member
from discord.ext.commands import Context

from db import db
from modules import bot

@bot.command()
async def diggities(ctx: Context):
    key = ctx.author.id
    current_balance = int(db.get(key)) if db.exists(key) else 0

    await ctx.author.send(f"You have '{current_balance}' diggities.")
    