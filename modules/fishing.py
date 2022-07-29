import os
import random
import asyncio
from enum import Enum
from typing import Dict

import emoji
from discord import Member
from discord.ext.commands import Context

from db import db
from modules import bot

from data import fish_json

MAX_TABLE_ROLL = 100
MIN_BITE_TIME = 3.0
MAX_BITE_TIME = 60.0
FISHING_COST = 1
TIME_TO_HOOK = 10.0


class FishingState(Enum):
    WAITING_FOR_BITE = 1
    FISH_BITING = 2
    HOOKING = 3


sessions: Dict[int, FishingState] = {}


async def _bite_timer(ctx: Context, fisher: int):
    time_to_bite = random.uniform(MIN_BITE_TIME, MAX_BITE_TIME)
    await asyncio.sleep(time_to_bite)

    if sessions[fisher] == FishingState.WAITING_FOR_BITE:
        sessions[fisher] = FishingState.FISH_BITING
        await ctx.send(f"**BITE!** {ctx.author.mention} has a fish on their line! Send **!hook** to catch.")
        await _hook_timer(ctx, fisher)
    else:
        # error??
        pass


async def _hook_timer(ctx: Context, fisher: int):
    await asyncio.sleep(TIME_TO_HOOK)

    if sessions[fisher] == FishingState.FISH_BITING:
        await ctx.send(f"{ctx.author.mention} Oh no. Seems it got away. Send **!fish** to recast.")
        del sessions[fisher]
    else:
        # error??
        pass


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
    fisher = ctx.author.id
    if fisher not in sessions:
        sessions[fisher] = FishingState.WAITING_FOR_BITE
        await ctx.send(f"{ctx.author.mention} You casts your line...")
        await _bite_timer(ctx, fisher)
    else:
        await ctx.send(f"{ctx.author.mention} You are already fishing.")


@bot.command()
async def hook(ctx: Context):
    fisher = ctx.author.id

    if fisher not in sessions:
        await ctx.send(f"{ctx.author.mention} You are not fishing right now. Send **!fish** to start fishing.")
    else:
        state = sessions[fisher]
        if state == FishingState.WAITING_FOR_BITE:
            await ctx.send(f"{ctx.author.mention} There was nothing on the line. Send **!fish** to recast.")
        elif state == FishingState.FISH_BITING:
            await _catch_fish(ctx)
            del sessions[fisher]
