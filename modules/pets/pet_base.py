import random

from discord.ext.commands import Context

from database.db import update_currency, get_currency
from modules import bot
from modules.pets.data import models, db_pets


@bot.command()
async def pet(ctx: Context):
    author = ctx.author
    author_id = author.id

    if not db_pets.check_pet(author):
        print(f"{ctx.author.name} does not have a pet yet.")
        await ctx.send(f"{author.mention} You do not have a pet yet.")
