import asyncio
import random
from enum import Enum
from typing import Dict

import emoji
from discord import Member, message, Guild, client
from discord.ext import tasks

from database.db import update_currency, get_currency
from modules import bot


RACE_START_TIMER = 120
START_TIMER_ALERT1 = 30
START_TIMER_ALERT2 = 10
START_TIMER_ALERT3 = 1


async def race(ctx):
    ctx.send("Ladies and gentlemen! A new race is about to begin!\n"
             f"Review the **!raceroster**, place your **!racebet n** (n = number of emoji), "
             f"and get ready for a show!")

    countdown = RACE_START_TIMER
    countdown_msg = ctx.send(f"Bets close in **{countdown}** seconds!")
    await asyncio.sleep(START_TIMER_ALERT1)

    for _ in range(0, 3):
        countdown -= START_TIMER_ALERT1
        await countdown_msg.edit(content=f"Bets close in **{countdown}** seconds!")

    for _ in range(0, 2):
        countdown -= START_TIMER_ALERT2
        await countdown_msg.edit(content=f"Bets close in **{countdown}** seconds!")

    for _ in range(0, 9):
        countdown -= START_TIMER_ALERT3
        await countdown_msg.edit(content=f"Bets close in **{countdown}** seconds!")

    await countdown_msg.edit(conteny="Bets are now closed!")


@bot.command()
async def startrace(ctx):
    await race(ctx)
