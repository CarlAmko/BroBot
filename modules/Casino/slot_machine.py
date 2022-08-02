import random

import emoji

from db import db
from modules import bot


SML_SLOT_COST = 1
MED_SLOT_COST = 5
LRG_SLOT_COST = 25
MAX_ROLL = 100
THRESHOLD_BASE = 50.1

awards = [1, 2, 4, 8, 16, 32, 64, 128, 256]


@bot.command()
async def slot(ctx):
    global awards

    selection = ctx.message.content.strip().lower()
    key: int = ctx.author.id
    payout = 0

    async def invalid():
        await ctx.send("Invalid slot machine. !slot x (x can be small, medium, or large)")

    roll1 = random.uniform(1,MAX_ROLL)
    roll2 = random.uniform(1,MAX_ROLL)
    roll3 = random.uniform(1,MAX_ROLL)

    if roll1 == roll2 == roll3:
        if roll1 > MAX_ROLL - (THRESHOLD_BASE / 256):
            payout += awards[8]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 128):
            payout += awards[7]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 64):
            payout += awards[6]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 32):
            payout += awards[5]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 16):
            payout += awards[4]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 8):
            payout += awards[3]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 4):
            payout += awards[2]
        elif roll1 > MAX_ROLL - (THRESHOLD_BASE / 2):
            payout += awards[1]
        else:
            payout += awards[0]

    if selection == "small":
        payout = payout - 1
    elif selection == "medium":
        payout = (payout * 5) - 5
    else:
        payout = (payout * 25) - 25

    current_balance = int(db.get(key)) if db.exists(key) else 0
    db.set(key, current_balance + payout)