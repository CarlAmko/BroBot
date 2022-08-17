from discord.ext.commands import Context

from database.db import get_currency, update_currency
from modules import bot

from enum import Enum


class AdminIds(Enum):
    spencer = 163686646829547521
    carl = 166218980028055554
    evan = 165649672252293120


@bot.command()
async def diggities(ctx: Context):
    key = ctx.author.id
    current_balance = get_currency(key)

    await ctx.send(f"{ctx.author.mention} has **{current_balance} BETA diggities**.")


@bot.command()
async def takemydiggities(ctx: Context):
    key = ctx.author.id

    current_balance = get_currency(key)
    await ctx.send(f"Thank you for the donation of **{current_balance} diggities**.")
    update_currency(key, - current_balance)


@bot.command()
async def testgrant(ctx: Context):
    key = ctx.author.id

    for id in AdminIds:
        if key == id.value:
            current_balance = get_currency(key)
            update_currency(key, 1000000)
            print(f"{ctx.author.name} received a test grant.")

@bot.command()
async def grant(ctx: Context):
    key = ctx.author.id

    current_balance = get_currency(key)
    if current_balance == 0:
        update_currency(key, 1000)
        await ctx.send(f"{ctx.author.mention} gets **1000 diggities**.")
    else:
        await ctx.send(f"{ctx.author.mention}, you got money. Why you asking for more?")


@bot.command()
async def resetdiggities(ctx: Context):
    key = int(ctx.message.content.split(' ', 1)[1].strip())
    current_balance = get_currency(key)
    user = await bot.fetch_user(key)
    print(f"{user.name}'s balance of {current_balance} set to 0")
    update_currency(key, -current_balance)
