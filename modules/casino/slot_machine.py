import asyncio
import random
from enum import Enum
from typing import Dict

import emoji

from database.db import update_currency, get_currency
from modules import bot
from modules.casino.data.db_casino import get_slot_jackpot, update_slot_jackpot
from modules.casino.data.models import JACKPOT_BASE, SlotMachineSizes

TIME_BETWEEN_ROLLS_MIN = 1.5
TIME_BETWEEN_ROLLS_MAX = 2
BONUS_LOAD_TIME = 3
WHEEL_SIZE = 28
BONUS_WHEEL_SIZE = 33

first_slot_wheel = [4, 2, 1, 3, 2, 5, 1, 4, 3, 5, 1, 2, 4, 7, 1, 4, 3, 6, 2, 1, 3, 2, 1, 5, 6, 2, 3, 1]
second_slot_wheel = [7, 1, 5, 2, 3, 1, 2, 6, 4, 1, 3, 2, 1, 5, 4, 3, 2, 1, 4, 3, 2, 1, 3, 4, 1, 2, 6, 5]
third_slot_wheel = [1, 4, 2, 1, 5, 3, 1, 2, 3, 4, 1, 2, 3, 1, 5, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 2, 6, 7]

broke_emj = emoji.emojize('<:cowboykermit:905608314786836551>')
spinning_emj = emoji.emojize('<a:slot:1004153272686358588>')
loading_emj = emoji.emojize("<a:loading:734622445910360105>")
nothing_emj = emoji.emojize("<:nothing:1004150080779059381>")
slot_emojis = [emoji.emojize('<:gottem:845463153331666984>'),
               emoji.emojize('<:jarjar:626517621038120989>'),
               emoji.emojize('<:kappamoon:635582648730779648>'),
               emoji.emojize('<:catthumbsup:630914661801263114>'),
               emoji.emojize('<:sittinthere:626254329535528960>'),
               emoji.emojize('<:jif:905509162920857651>'),
               emoji.emojize('<:Booba:981416672831361074>')]
first_bonus_emojis = [emoji.emojize("<:plus_sign:1005053410556518480>"),
                      emoji.emojize(":x:")]
second_bonus_emojis = [emoji.emojize(":two:"),
                       emoji.emojize(":five:"),
                       emoji.emojize(":keycap_ten:"),
                       emoji.emojize("<:hundred:1005055991370489906>"),
                       emoji.emojize("<:d4:626254888795635713>")]
d_four_emojis = [emoji.emojize(":one:"),
                 emoji.emojize(":two:"),
                 emoji.emojize(":three:"),
                 emoji.emojize(":four:")]


class SlotMachine:
    in_use: bool
    last_message = None
    pay_lines = []


class Symbols(Enum):
    gottem = 1
    jarjar = 2
    kappamoon = 3
    catthumbsup = 4
    sittinthere = 5
    jif = 6
    booba = 7


class BonusSymbols(Enum):
    plus_five = 1
    plus_ten = 2
    plus_hundred = 3
    times_die = 4
    times_two = 5
    times_five = 6
    times_ten = 7


machines: Dict[int, SlotMachine] = {}


def check_rows(wheels, key: int):
    for i in range(0, 3):
        if machines[key].pay_lines[i] == 0 and wheels[0][i] == wheels[1][i] == wheels[2][i]:
            machines[key].pay_lines[i] = wheels[0][i]


def check_diagonals(wheels, key: int):
    if machines[key].pay_lines[3] == 0 and wheels[0][0] == wheels[1][1] == wheels[2][2]:
        machines[key].pay_lines[3] = wheels[0][0]
    if machines[key].pay_lines[4] == 0 and wheels[0][2] == wheels[1][1] == wheels[2][0]:
        machines[key].pay_lines[4] = wheels[0][2]


def calculate_winnings(slot_id: str, key: int) -> int:
    winnings = 0

    for val in machines[key].pay_lines:
        if val == Symbols.gottem.value:
            winnings += 2
        elif val == Symbols.jarjar.value:
            winnings += 5
        elif val == Symbols.kappamoon.value:
            winnings += 20
        elif val == Symbols.catthumbsup.value:
            winnings += 50
        elif val == Symbols.sittinthere.value:
            winnings += 200
        elif val == Symbols.jif.value:
            winnings += 500
        elif val == Symbols.booba.value:
            jackpot = get_slot_jackpot(slot_id)
            multiplier = int(slot_id.replace('7', ''))
            update_slot_jackpot(slot_id, JACKPOT_BASE * multiplier)
            winnings += jackpot

    return winnings


def spin_bonus_wheel() -> int:
    roll = random.randint(1, BONUS_WHEEL_SIZE)

    if roll <= 12:
        return BonusSymbols.plus_five.value
    elif roll <= 20:
        return BonusSymbols.plus_ten.value
    elif roll <= 24:
        return BonusSymbols.plus_hundred.value
    elif roll <= 27:
        return BonusSymbols.times_die.value
    elif roll <= 30:
        return BonusSymbols.times_two.value
    elif roll <= 32:
        return BonusSymbols.times_five.value
    else:
        return BonusSymbols.times_ten.value


def get_first_bonus_emoji(bonus: int):
    if bonus <= BonusSymbols.plus_hundred.value:
        first_emj = first_bonus_emojis[0]
    else:
        first_emj = first_bonus_emojis[1]

    return first_emj


def get_second_bonus_emoji(bonus: int):
    if bonus == BonusSymbols.times_two.value:
        second_emj = second_bonus_emojis[0]
    elif bonus == BonusSymbols.plus_five.value or bonus == BonusSymbols.times_five.value:
        second_emj = second_bonus_emojis[1]
    elif bonus == BonusSymbols.plus_ten.value or bonus == BonusSymbols.times_ten.value:
        second_emj = second_bonus_emojis[2]
    elif bonus == BonusSymbols.plus_hundred.value:
        second_emj = second_bonus_emojis[3]
    else:
        second_emj = second_bonus_emojis[4]

    return second_emj


def adjust_winnings(payout: int, bonus: int, die_roll=1):
    if bonus == BonusSymbols.plus_five.value:
        print("plus 5")
        payout += 5
    elif bonus == bonus == BonusSymbols.plus_ten.value:
        print("plus 10")
        payout += 10
    elif bonus == bonus == BonusSymbols.plus_hundred.value:
        print("plus 100")
        payout += 100
    elif bonus == bonus == BonusSymbols.times_die.value:
        print(f"times 1d4:{die_roll}")
        payout *= die_roll
    elif bonus == bonus == BonusSymbols.times_two.value:
        print("times 2")
        payout *= 2
    elif bonus == bonus == BonusSymbols.times_five.value:
        print("times 5")
        payout *= 5
    else:
        print("times 10")
        payout *= 10

    return payout


@bot.command()
async def slot(ctx):
    slot_size = ctx.message.content.split()[1].strip().lower()
    wager = int(ctx.message.content.split()[2].strip())
    key = int(ctx.author.id)
    await ctx.message.delete()

    if key in machines:
        if machines[key].in_use:
            await ctx.send(f"{ctx.author.mention}, you are already playing. "
                           f"Please wait for your current slot to finish.")
            return
    else:
        machines[key] = SlotMachine()
        machines[key].in_use = True

    machines[key].pay_lines = [-1, -1, -1, -1, -1]
    bonus_active = False

    if wager == 1:
        machines[key].pay_lines[1] = 0
    elif wager == 2:
        machines[key].pay_lines[0], machines[key].pay_lines[1], machines[key].pay_lines[2] = 0, 0, 0
    elif wager == 3:
        machines[key].pay_lines[0], machines[key].pay_lines[1], machines[key].pay_lines[2] = 0, 0, 0
        machines[key].pay_lines[3], machines[key].pay_lines[4] = 0, 0
    elif wager == 4:
        machines[key].pay_lines[0], machines[key].pay_lines[1], machines[key].pay_lines[2] = 0, 0, 0
        machines[key].pay_lines[3], machines[key].pay_lines[4] = 0, 0
        bonus_active = True
    else:
        machines[key].in_use = False
        await ctx.send(f"{ctx.author.mention} Invalid slot command. **!slot x n** (x can be small, medium, or large;"
                       f" n is your wager can be 1, 2, 3, or 4)")
        return

    if slot_size == "sm":
        slot_id = SlotMachineSizes.sml.generate_key
        cost = SlotMachineSizes.sml.value
    elif slot_size == "med":
        slot_id = SlotMachineSizes.med.generate_key
        cost = SlotMachineSizes.med.value
    elif slot_size == "lg":
        slot_id = SlotMachineSizes.lrg.generate_key
        cost = SlotMachineSizes.lrg.value
    else:
        machines[key].in_use = False
        await ctx.send(f"{ctx.author.mention} Invalid slot command. **!slot x n** (x can be sm, med, or lg;"
                       f" n is your wager can be 1, 2, 3, or 4)")
        return

    current_balance = get_currency(key)
    print(f"{ctx.author.name} plays the {slot_size} slot wagering {wager} with a starting balance of {current_balance}")
    if current_balance >= cost * wager:
        update_currency(key, -(cost * wager))
        update_slot_jackpot(slot_id, cost * wager)
    else:
        machines[key].in_use = False
        await ctx.send(f"{broke_emj} Woah there {ctx.author.mention}! You best come back when you've got more "
                       f"diggities.")
        return

    if not machines[key].last_message is None:
        await machines[key].last_message.delete()

    title_content = f"{ctx.author.mention} is playing the {slot_size} slot with a wager of **{wager}**\n"
    current_msg = await ctx.send(title_content)
    machines[key].last_message = current_msg

    wheel_content = f"{spinning_emj}{spinning_emj}{spinning_emj}\n" \
                    f"{spinning_emj}{spinning_emj}{spinning_emj}\n" \
                    f"{spinning_emj}{spinning_emj}{spinning_emj}\n"

    await current_msg.edit(content=(title_content + wheel_content))

    roll = random.randint(0, WHEEL_SIZE - 1)
    first_wheel = [first_slot_wheel[roll - 2], first_slot_wheel[roll - 1], first_slot_wheel[roll]]
    first_wheel_emj = [slot_emojis[first_wheel[0] - 1], slot_emojis[first_wheel[1] - 1],
                       slot_emojis[first_wheel[2] - 1]]

    await asyncio.sleep(random.uniform(TIME_BETWEEN_ROLLS_MIN, TIME_BETWEEN_ROLLS_MAX))
    wheel_content = f"{first_wheel_emj[0]}{spinning_emj}{spinning_emj}\n" \
                    f"{first_wheel_emj[1]}{spinning_emj}{spinning_emj}\n" \
                    f"{first_wheel_emj[2]}{spinning_emj}{spinning_emj}\n"

    await current_msg.edit(content=(title_content + wheel_content))

    roll = random.randint(0, WHEEL_SIZE - 1)
    second_wheel = [second_slot_wheel[roll - 2], second_slot_wheel[roll - 1], second_slot_wheel[roll]]
    second_wheel_emj = [slot_emojis[second_wheel[0] - 1], slot_emojis[second_wheel[1] - 1],
                        slot_emojis[second_wheel[2] - 1]]
    await asyncio.sleep(random.uniform(TIME_BETWEEN_ROLLS_MIN, TIME_BETWEEN_ROLLS_MAX))
    wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{spinning_emj}\n" \
                    f"{first_wheel_emj[1]}{second_wheel_emj[1]}{spinning_emj}\n" \
                    f"{first_wheel_emj[2]}{second_wheel_emj[2]}{spinning_emj}\n"

    await current_msg.edit(content=(title_content + wheel_content))

    roll = random.randint(0, WHEEL_SIZE - 1)
    third_wheel = [third_slot_wheel[roll - 2], third_slot_wheel[roll - 1], third_slot_wheel[roll]]
    third_wheel_emj = [slot_emojis[third_wheel[0] - 1], slot_emojis[third_wheel[1] - 1],
                       slot_emojis[third_wheel[2] - 1]]
    await asyncio.sleep(random.uniform(TIME_BETWEEN_ROLLS_MIN, TIME_BETWEEN_ROLLS_MAX))
    wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{third_wheel_emj[0]}\n" \
                    f"{first_wheel_emj[1]}{second_wheel_emj[1]}{third_wheel_emj[1]}\n" \
                    f"{first_wheel_emj[2]}{second_wheel_emj[2]}{third_wheel_emj[2]}\n"

    await current_msg.edit(content=(title_content + wheel_content))

    print(f"{first_wheel[0]} {second_wheel[0]} {third_wheel[0]}\n"
          f"{first_wheel[1]} {second_wheel[1]} {third_wheel[1]}\n"
          f"{first_wheel[2]} {second_wheel[2]} {third_wheel[2]}\n")

    wheels = [first_wheel, second_wheel, third_wheel]
    check_rows(wheels, key)
    check_diagonals(wheels, key)
    payout = calculate_winnings(slot_id, key)

    if bonus_active and payout > 0:
        wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{third_wheel_emj[0]}\n" \
                        f"{first_wheel_emj[1]}{second_wheel_emj[1]}{third_wheel_emj[1]}{spinning_emj}\n" \
                        f"{first_wheel_emj[2]}{second_wheel_emj[2]}{third_wheel_emj[2]}\n"

        await current_msg.edit(content=(title_content + wheel_content))

        await asyncio.sleep(BONUS_LOAD_TIME)
        bonus = spin_bonus_wheel()
        print(bonus)
        first_bonus_emj = get_first_bonus_emoji(bonus)

        wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{third_wheel_emj[0]}\n" \
                        f"{first_wheel_emj[1]}{second_wheel_emj[1]}{third_wheel_emj[1]}{first_bonus_emj}" \
                        f"{loading_emj}\n" \
                        f"{first_wheel_emj[2]}{second_wheel_emj[2]}{third_wheel_emj[2]}\n"

        await current_msg.edit(content=(title_content + wheel_content))
        await asyncio.sleep(BONUS_LOAD_TIME)
        second_bonus_emj = get_second_bonus_emoji(bonus)

        if not bonus == BonusSymbols.times_die.value:
            wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{third_wheel_emj[0]}\n" \
                            f"{first_wheel_emj[1]}{second_wheel_emj[1]}{third_wheel_emj[1]}{first_bonus_emj}" \
                            f"{second_bonus_emj}\n" \
                            f"{first_wheel_emj[2]}{second_wheel_emj[2]}{third_wheel_emj[2]}\n"

            await current_msg.edit(content=(title_content + wheel_content))
            payout = adjust_winnings(payout, bonus)

        else:
            wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{third_wheel_emj[0]}\n" \
                            f"{first_wheel_emj[1]}{second_wheel_emj[1]}{third_wheel_emj[1]}{first_bonus_emj}" \
                            f"{second_bonus_emj}{loading_emj}\n" \
                            f"{first_wheel_emj[2]}{second_wheel_emj[2]}{third_wheel_emj[2]}\n"

            await current_msg.edit(content=(title_content + wheel_content))
            await asyncio.sleep(BONUS_LOAD_TIME)
            die_roll = random.randint(1, 4)

            wheel_content = f"{first_wheel_emj[0]}{second_wheel_emj[0]}{third_wheel_emj[0]}\n" \
                            f"{first_wheel_emj[1]}{second_wheel_emj[1]}{third_wheel_emj[1]}{first_bonus_emj}" \
                            f"{second_bonus_emj}{d_four_emojis[die_roll - 1]}\n" \
                            f"{first_wheel_emj[2]}{second_wheel_emj[2]}{third_wheel_emj[2]}\n"

            await current_msg.edit(content=(title_content + wheel_content))
            payout = adjust_winnings(payout, bonus, die_roll)

    if payout > 0:
        payout *= cost
        award_content = f"{ctx.author.mention} was awarded **{payout} diggities**!"
        await current_msg.edit(content=(title_content + wheel_content + award_content))
    else:
        award_content = f"{ctx.author.mention} didn't win anything. Better luck next time."
        await current_msg.edit(content=(title_content + wheel_content + award_content))

    print(f"Awarded: {payout}")
    update_currency(key, payout)
    machines[key].in_use = False


@bot.command()
async def slotawards(ctx):
    # await ctx.message.delete()
    msg = f"{slot_emojis[6]}{slot_emojis[6]}{slot_emojis[6]} | **JACKPOT**\n" \
          f"{slot_emojis[5]}{slot_emojis[5]}{slot_emojis[5]} | **500**\n" \
          f"{slot_emojis[4]}{slot_emojis[4]}{slot_emojis[4]} | **200**\n" \
          f"{slot_emojis[3]}{slot_emojis[3]}{slot_emojis[3]} | **50**\n" \
          f"{slot_emojis[2]}{slot_emojis[2]}{slot_emojis[2]} | **20**\n" \
          f"{slot_emojis[1]}{slot_emojis[1]}{slot_emojis[1]} | **5**\n" \
          f"{slot_emojis[0]}{slot_emojis[0]}{slot_emojis[0]} | **2**\n" \
          f"{nothing_emj}{nothing_emj}{nothing_emj}\n" \
          f"If you wagered 4 and you win on a payline you get a bonus round!\n" \
          f"**Bonus Round Outcomes:**\n" \
          f" - Plus 5 to your winnings\n" \
          f" - Plus 10 to your winnings\n" \
          f" - Plus 100 to your winnings\n" \
          f" - 1d4 times your winnings\n" \
          f" - 2 times your winnings\n" \
          f" - 5 times your winnings\n" \
          f" - 10 times your winnings\n" \
          f"{nothing_emj}{nothing_emj}{nothing_emj}\n" \
          f"Remember that all winnings are multiplied by the cost of the machine."

    await ctx.send(msg)


@bot.command()
async def slothelp(ctx):
    # await ctx.message.delete()
    msg = "**SLOTS INFO**\n" \
          " - wager minimum is 1 and maximum is 4\n" \
          "         - wager 1 to play center horizontal payline only\n" \
          "         - wager 2 unlocks the top and bottom horizontal paylines\n" \
          "         - wager 3 unlocks both diagonal paylines\n" \
          "         - wager 4 unlocks the bonus wheel (bonus wheel only occurs if there is a win on a payline)\n" \
          " - !slot sm n - cost 1 diggity per wager\n" \
          " - !slot med n - cost 25 diggities per wager\n" \
          " - !slot lg n - cost 100 diggities per wager\n" \
          " - !slotjackpot x - (x = sm, med, or lg) check the current jackpot\n" \
          " - !slotawards - shows awards from slots\n" \
          " - !grant - grants 10 diggities if you have 0\n" \
          " - !takemydiggities - **WARNING** this will set your diggity balance for the beta to 0\n" \
          " - !diggitiesbeta - sends your diggity balance for the beta"

    await ctx.send(f"{ctx.author.mention}\n{msg}")


@bot.command()
async def slotjackpot(ctx):
    slot_size = ctx.message.content.split()[1].strip().lower()
    # await ctx.message.delete()

    if not (slot_size == "sm" or slot_size == "med" or slot_size == "lg"):
        await ctx.send(f"{ctx.author.mention} Invalid slot command. **!slotjackpot x** (x can be sm, med, or lg)")
        return

    slot_id = SlotMachineSizes.sml.generate_key \
        if slot_size == "sm" else (SlotMachineSizes.med.generate_key
                                   if slot_size == "med" else SlotMachineSizes.lrg.generate_key)

    jackpot = get_slot_jackpot(slot_id)

    await ctx.send(f"The current jackpot for the {slot_size} slot is **{jackpot} diggities**!")


@bot.command()
async def resetjackpot(ctx):
    slot_size = ctx.message.content.split()[1].strip().lower()
    await ctx.message.delete()

    if not (slot_size == "sm" or slot_size == "med" or slot_size == "lg"):
        return

    slot_id = SlotMachineSizes.sml.generate_key \
        if slot_size == "sm" else (SlotMachineSizes.med.generate_key
                                   if slot_size == "med" else SlotMachineSizes.lrg.generate_key)

    current_jackpot = get_slot_jackpot(slot_id)
    update_slot_jackpot(slot_id, -current_jackpot)
    multiplier = int(slot_id.replace('7', ''))
    update_slot_jackpot(slot_id, JACKPOT_BASE * multiplier)
