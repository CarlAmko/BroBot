import random
import asyncio

import emoji
from discord import Member
from discord.ext.commands import Context

from db import db
from modules import bot


MAX_TABLE_ROLL = 100
MIN_BITE_TIME = 3.0
MAX_BITE_TIME = 60.0
FISHING_COST = 1
TIME_TO_HOOK = 10.0

NOT_FISHING = 0
WAITING_FOR_BITE = 1
FISH_BITING = 2
HOOKING = 3

sessions = []

boot = emoji.emojize(':boot:')  # 1 - 10 0d
common_fish = emoji.emojize(':fish:')  # 11 - 55 2d
shrimp = emoji.emojize(':shrimp:')  # 56 - 77 1d
blow_fish = emoji.emojize(':blowfish:')  # 78 - 88 5d
tropical_fish = emoji.emojize(':tropical_fish:')  # 89 - 97 10d
shark = emoji.emojize(':shark:')  # 98 - 100 100d


class FishingSession:
    id: int
    state: int


async def _bite_timer(ctx: Context, fisher: int):

    time_to_bite = random.uniform(MIN_BITE_TIME, MAX_BITE_TIME)
    await asyncio.sleep(time_to_bite)

    if sessions[fisher].state == WAITING_FOR_BITE:
        sessions[fisher].state = FISH_BITING
        await ctx.send(f"**BITE!** {ctx.author.mention} has a fish on their line! Send **!hook** to catch.")
        await _hook_timer(ctx, fisher)


async def _hook_timer(ctx: Context, fisher: int):

    await asyncio.sleep(TIME_TO_HOOK)

    if sessions[fisher].state == FISH_BITING:
        await ctx.send(f"{ctx.author.mention} Oh no. Seems it got away. Send **!fish** to recast.")
        sessions.remove(fisher)


async def _catch_fish(ctx):
    fish_roll = random.randint(1, MAX_TABLE_ROLL)

    if fish_roll <= 10:
        await ctx.send(f"{boot}")
        await ctx.send(f"{ctx.author.mention} caught a boot... Sold for **0 diggities**.")
    elif 10 < fish_roll <= 55:
        await ctx.send(f"{common_fish}")
        await ctx.send(f"{ctx.author.mention} caught a fish. Sold for **2 diggities**.")
    elif 55 < fish_roll <= 77:
        await ctx.send(f"{shrimp}")
        await ctx.send(f"{ctx.author.mention} caught a shrimp. Sold for **1 diggity**.")
    elif 77 < fish_roll <= 88:
        await ctx.send(f"{blow_fish}")
        await ctx.send(f"{ctx.author.mention} caught a blow fish! Sold for **5 diggities**.")
    elif 88 < fish_roll <= 97:
        await ctx.send(f"{tropical_fish}")
        await ctx.send(f"{ctx.author.mention} caught a tropical fish! Sold for **10 diggities**.")
    else:
        await ctx.send(f"{shark}")
        await ctx.send(f"{ctx.author.mention}**CAUGHT A SHARK!** Sold for **100 diggities**.")


@bot.command()
async def fish(ctx: Context):

    new_fisher = True

    for i in range(len(sessions)):
        if ctx.author.id == sessions[i].id:
            if not sessions[i].state == NOT_FISHING:
                await ctx.send(f"{ctx.author.mention} You are already fishing.")
                return

            fisher = i
            sessions[i].state = WAITING_FOR_BITE
            new_fisher = False
            break

    if new_fisher:
        fisher = len(sessions)
        sessions.append(FishingSession)
        sessions[fisher].id = ctx.author.id

    sessions[fisher].state = WAITING_FOR_BITE
    await ctx.send(f"{ctx.author.mention} You casts your line...")
    await _bite_timer(ctx, fisher)


@bot.command()
async def hook(ctx: Context):

    for i in range(len(sessions)):
        if ctx.author.id == sessions[i].id:
            if sessions[i].state == WAITING_FOR_BITE:
                await ctx.send(f"{ctx.author.mention} There was nothing on the line. Send **!fish** to recast.")
                sessions[i].state = NOT_FISHING
                return
            elif sessions[i].state == NOT_FISHING or sessions[i].state == HOOKING:
                await ctx.send(f"{ctx.author.mention} You are not fishing right now. Send **!fish** to start fishing.")
                return
            else:
                sessions[i].state = NOT_FISHING
                await _catch_fish(ctx)
                return
