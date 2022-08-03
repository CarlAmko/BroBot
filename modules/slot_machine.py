import asyncio
import random
from enum import Enum

import emoji

from db import db
from modules import bot


MAX_ROLL = 100
PROB_BASE = 70
PROB_REDUCTION = 25
PROB_REDUCTION_OFFSET = 1
TIME_BETWEEN_ROLLS_MIN = 1.5
TIME_BETWEEN_ROLLS_MAX = 2
AWARD_POWER = 3

selections = [0, 27, 47, 65, 80, 90, 95, 98, 99.5]

broke_emj = emoji.emojize('<:cowboykermit:905608314786836551>')
spinning_emj = emoji.emojize('<a:slot:1004153272686358588>')
slot_emojis = [emoji.emojize('<:gottem:845463153331666984>'),
               emoji.emojize('<:jarjar:626517621038120989>'),
               emoji.emojize('<:fry:628312618049994782>'),
               emoji.emojize('<:kappamoon:635582648730779648>'),
               emoji.emojize('<:catthumbsup:630914661801263114>'),
               emoji.emojize('<:sittinthere:626254329535528960>'),
               emoji.emojize('<:puffin:670032154998079518>'),
               emoji.emojize('<:jif:905509162920857651>'),
               emoji.emojize('<:Booba:981416672831361074>')]


class PayoutMultiplier(Enum):
    sml = 1
    med = 5
    lrg = 25


class Thresholds(Enum):
    gottem = 0
    jarjar = 1
    fry = 2
    kappamoon = 3
    catthumbsup = 4
    sittinthere = 5
    puffin = 6
    jif = 7
    booba = 8

    @property
    def selection(self):
        return selections[self.value]


@bot.command()
async def slot(ctx):
    selection = ctx.message.content.split(' ', 1)[1].strip().lower()
    key: int = ctx.author.id
    payout = 0

    if selection == "small":
        payout_multiplier = PayoutMultiplier.sml.value
    elif selection == "medium":
        payout_multiplier = PayoutMultiplier.med.value
    elif selection == "large":
        payout_multiplier = PayoutMultiplier.lrg.value
    else:
        await ctx.send("Invalid slot machine. !slot x (x can be small, medium, or large)")
        return

    current_balance = int(db.get(key)) if db.exists(key) else 0
    print(f"{ctx.author.name} plays the {selection} slot with a starting balance of {current_balance}")
    if current_balance >= payout_multiplier:
        new_balance = current_balance - payout_multiplier
    else:
        await ctx.send(f"{broke_emj} Woah there {ctx.author.mention}! You best come back when you've got more diggities.")
        return

    await ctx.send(f"{ctx.author.mention} plays the **{payout_multiplier} diggity** slot:")
    message = await ctx.send(f"{spinning_emj}{spinning_emj}{spinning_emj}")

    first_roll = get_first_roll(random.uniform(1, MAX_ROLL))
    print(f"First roll: {first_roll}")
    first_rolled_emoji = slot_emojis[first_roll]
    await asyncio.sleep(random.uniform(TIME_BETWEEN_ROLLS_MIN,TIME_BETWEEN_ROLLS_MAX))
    await message.edit(content=f"{first_rolled_emoji}{spinning_emj}{spinning_emj}")

    second_roll = get_next_roll(first_roll)
    print(f"Second roll: {second_roll}")
    second_rolled_emoji = slot_emojis[second_roll]
    await asyncio.sleep(random.uniform(TIME_BETWEEN_ROLLS_MIN,TIME_BETWEEN_ROLLS_MAX))
    await message.edit(content=f"{first_rolled_emoji}{second_rolled_emoji}{spinning_emj}")

    third_roll = get_next_roll(second_roll)
    print(f"Third roll: {third_roll}")
    third_rolled_emoji = slot_emojis[third_roll]
    await asyncio.sleep(TIME_BETWEEN_ROLLS_MAX)
    await message.edit(content=f"{first_rolled_emoji}{second_rolled_emoji}{third_rolled_emoji}")

    if first_roll == second_roll == third_roll:
        payout = payout_multiplier * (AWARD_POWER ** first_roll)
        await ctx.send(f"{ctx.author.mention} was awarded **{payout} diggities**!")
    else:
        await ctx.send(f"{ctx.author.mention} didn't win anything. Better luck next time.")

    print(f"Awarded: {payout}")
    db.set(key, new_balance + payout)


def get_first_roll(roll):
    first_selection = None
    print(f"First selection: {roll}")

    for threshold in Thresholds:
        if roll >= threshold.selection:
            first_selection = threshold.value
        else:
            break

    return first_selection


def get_next_roll(previous_roll):
    roll = random.uniform(1, MAX_ROLL)
    print(f"Roll for match: {roll}")

    tracker = 1
    result = PROB_BASE
    while tracker <= previous_roll:
        result -= (PROB_REDUCTION * (1 / (tracker ** PROB_REDUCTION_OFFSET)))
        tracker += 1

    print(f"Reach to match: {MAX_ROLL - result}")
    if roll >= MAX_ROLL - result:
        next_selection = previous_roll
    else:
        next_selection = random.choice([i for i in range(0, 9) if not i == previous_roll])

    return next_selection


@bot.command()
async def slotawards(ctx):
    index = 0
    msg = ""
    for emj in slot_emojis:
        msg += f"{emj}{emj}{emj} **small = {(AWARD_POWER ** index) * 1}  |  medium = {(AWARD_POWER ** index) * 5}" \
               f"  |  large = {(AWARD_POWER ** index) * 25}**\n"
        index += 1

    await ctx.send(msg)
