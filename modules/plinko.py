import asyncio
import random
from typing import List

from modules import bot
from discord.ext.commands import Context
from discord import Message
import emoji
from database.db import db

MIN_OUTCOMES = 2
MAX_OUTCOMES = 20
LITE_MIN_OUTCOMES = 2
LITE_MAX_OUTCOMES = 20

meatball_emj = emoji.emojize('<:meatball:987726586637869146>')
nothing_emj = emoji.emojize('<:nothing:1004150080779059381>')
peg_emj = emoji.emojize(':white_small_square:')
wall_emj = emoji.emojize(':white_large_square:')
slot_emj = emoji.emojize(':white_square_button:')
question_mark_emj = emoji.emojize('<a:Question:1013338384531456063>')
bomb_emoji = emoji.emojize(':bomb:')
number_emjs = [
    emoji.emojize('<a:1_:1013340616912019486>'),
    emoji.emojize('<a:2_:1013340626462461962>'),
    emoji.emojize('<a:3_:1013340624918937680>'),
    emoji.emojize('<a:4_:1013340623010549791>'),
    emoji.emojize('<a:5_:1013340621588672562>'),
    emoji.emojize('<a:6_:1013340615133626379>'),
    emoji.emojize('<a:7_:1013340618803642388>'),
    emoji.emojize('<a:8_:1013340620175196210>'),
    emoji.emojize('<a:9_:1013340612147302411>'),
    emoji.emojize('<a:10:1013340474469253260>'),
    emoji.emojize('<a:11:1013339520374157322>'),
    emoji.emojize('<a:12:1013346025114697758>'),
    emoji.emojize('<a:13:1013346023281799198>'),
    emoji.emojize('<a:14:1013346020740050976>'),
    emoji.emojize('<a:15:1013346019217518692>'),
    emoji.emojize('<a:16:1013346017472675890>'),
    emoji.emojize('<a:17:1013346015736234035>'),
    emoji.emojize('<a:18:1013346013865578497>'),
    emoji.emojize('<a:19:1013346012435337216>'),
    emoji.emojize('<a:20:1013346026792427550>')
]
letter_emjs = [
    emoji.emojize('<a:A_:1013338405788209153>'),
    emoji.emojize('<a:B_:1013338400218157066>'),
    emoji.emojize('<a:C_:1013338395486994523>'),
    emoji.emojize('<a:D_:1013338396837564457>'),
    emoji.emojize('<a:E_:1013338410129305671>'),
    emoji.emojize('<a:F_:1013338392131551232>'),
    emoji.emojize('<a:G_:1013338393721188443>'),
    emoji.emojize('<a:H_:1013338411437924433>'),
    emoji.emojize('<a:I_:1013338386070782053>'),
    emoji.emojize('<a:J_:1013338418232709141>'),
    emoji.emojize('<a:K_:1013338390902607892>'),
    emoji.emojize('<a:L_:1013338417112817674>'),
    emoji.emojize('<a:M_:1013338387832393728>'),
    emoji.emojize('<a:N_:1013338389283610754>'),
    emoji.emojize('<a:O_:1013338420657016925>'),
    emoji.emojize('<a:P_:1013338398234247219>'),
    emoji.emojize('<a:Q_:1013338404466991196>'),
    emoji.emojize('<a:R_:1013338414403289180>'),
    emoji.emojize('<a:S_:1013338415560925236>'),
    emoji.emojize('<a:T_:1013338407310741545>'),
    emoji.emojize('<a:U_:1013338401497423894>'),
    emoji.emojize('<a:V_:1013338408808095824>'),
    emoji.emojize('<a:W_:1013338422515081257>'),
    emoji.emojize('<a:X_:1013338403057717339>'),
    emoji.emojize('<a:Y_:1013338412805279765>'),
    emoji.emojize('<a:Z_:1013338419604238388>')
]

is_active: bool = False
outcomes: int
total_columns: int

lite_is_active: bool = False
lite_outcomes: int
lite_total_columns: int
lite_msgs: List[str]


async def print_board(ctx: Context) -> List[Message]:
    global outcomes, total_columns

    def empty_row() -> str:
        msg = f"{wall_emj}"
        for _ in range(total_columns - 2):
            msg += f"{nothing_emj}"
        msg += f"{wall_emj}\n"
        return msg

    def sm_peg_row() -> str:
        msg = f"{wall_emj}{nothing_emj}"
        for _ in range(outcomes - 1):
            msg += f"{peg_emj}{nothing_emj}"
        msg += f"{wall_emj}.\n"
        return msg

    def lrg_peg_row() -> str:
        msg = f"{wall_emj}"
        for _ in range(outcomes - 1):
            msg += f"{peg_emj}{nothing_emj}"
        msg += f"{peg_emj}{wall_emj}.\n"
        return msg

    msgs = []

    header_text = ""
    for _ in range(int((total_columns - 1) / 2) - 1):
        header_text += f"{nothing_emj}"
    header_text += f"{meatball_emj}\n"
    for _ in range(int((total_columns - 1) / 2) - 1):
        header_text += f"{nothing_emj}"
    header_text += f"\n{wall_emj}{wall_emj}"
    for i in range(outcomes - 1):
        header_text += f"{letter_emjs[i]}{wall_emj}"
    header_text += f"{wall_emj}.\n"
    msgs.append(await ctx.send(header_text))

    if (outcomes % 2) == 0:
        num_peg_rows = outcomes - 1
    else:
        num_peg_rows = outcomes

    lrg_row = False
    for _ in range(num_peg_rows):
        msg_text = empty_row()
        if lrg_row:
            msg_text += lrg_peg_row()
        else:
            msg_text += sm_peg_row()
        msgs.append(await ctx.send(msg_text))
        lrg_row = not lrg_row

    outcomes_text = f"{wall_emj}"
    for _ in range(outcomes):
        outcomes_text += f"{slot_emj}{wall_emj}"
    outcomes_text += f"\n{nothing_emj}"
    for i in range(outcomes):
        outcomes_text += f"{number_emjs[i]}{nothing_emj}"
    outcomes_text += "."
    msgs.append(await ctx.send(outcomes_text))

    for i in range(outcomes - 1):
        await msgs[-1].add_reaction(letter_emjs[i])
    await msgs[-1].add_reaction(question_mark_emj)

    return msgs


async def drop_ball(msgs: List[Message], current_column: int) -> int:
    global outcomes, total_columns

    def empty_row(meatball: bool) -> str:
        msg = f"{wall_emj}"
        if meatball:
            for j in range(total_columns - 2):
                if j + 1 == current_column - 1:
                    msg += f"{meatball_emj}"
                else:
                    msg += f"{nothing_emj}"
            msg += f"{wall_emj}\n"
        else:
            for _ in range(total_columns - 2):
                msg += f"{nothing_emj}"
            msg += f"{wall_emj}\n"
        return msg

    def sm_peg_row(meatball: bool) -> str:
        if meatball:
            msg = f"{wall_emj}"
            if space_num == 1:
                msg += f"{meatball_emj}"
            else:
                msg += f"{nothing_emj}"
            for j in range(outcomes - 1):
                if j + 1 == space_num - 1:
                    msg += f"{peg_emj}{meatball_emj}"
                else:
                    msg += f"{peg_emj}{nothing_emj}"
            msg += f"{wall_emj}.\n"
        else:
            msg = f"{wall_emj}{nothing_emj}"
            for _ in range(outcomes - 1):
                msg += f"{peg_emj}{nothing_emj}"
            msg += f"{wall_emj}.\n"
        return msg

    def lrg_peg_row(meatball: bool) -> str:
        if meatball:
            msg = f"{wall_emj}"
            for j in range(outcomes - 1):
                if j + 1 == space_num :
                    msg += f"{peg_emj}{meatball_emj}"
                else:
                    msg += f"{peg_emj}{nothing_emj}"
            msg += f"{peg_emj}{wall_emj}.\n"
        else:
            msg = f"{wall_emj}"
            for _ in range(outcomes - 1):
                msg += f"{peg_emj}{nothing_emj}"
            msg += f"{peg_emj}{wall_emj}.\n"
        return msg

    print(f"starting column: {current_column}")

    header_text = f"{nothing_emj}\n"
    for _ in range(current_column - 1):
        header_text += f"{nothing_emj}"
    header_text += f"{meatball_emj}\n{wall_emj}{wall_emj}"
    for i in range(outcomes - 1):
        header_text += f"{letter_emjs[i]}{wall_emj}"
    header_text += f"{wall_emj}.\n"
    await msgs[0].edit(content=header_text)

    await asyncio.sleep(1)

    header_text = ""
    for _ in range(outcomes):
        header_text += f"{nothing_emj}"
    header_text += f"{nothing_emj}\n"
    for _ in range(outcomes):
        header_text += f"{nothing_emj}"
    header_text += f"\n{wall_emj}{wall_emj}"
    for i in range(outcomes - 1):
        if i + 1 == int((current_column - 1) / 2):
            header_text += f"{meatball_emj}{wall_emj}"
        else:
            header_text += f"{letter_emjs[i]}{wall_emj}"
    header_text += f"{wall_emj}.\n"
    await msgs[0].edit(content=header_text)

    await asyncio.sleep(1)

    lrg_row = False
    for i in range(len(msgs) - 2):
        await asyncio.sleep(1)

        msg_text = empty_row(True)
        if current_column == 2:
            current_column += 1
        elif current_column == outcomes * 2:
            current_column -= 1
        else:
            current_column += random.choice([-1, 1])
        print(f"moved to: {current_column}")

        if lrg_row:
            msg_text += lrg_peg_row(False)
        else:
            msg_text += sm_peg_row(False)
        await msgs[i + 1].edit(content=msg_text)

        if i > 0:
            msg_text = empty_row(False)
            if not lrg_row:
                msg_text += lrg_peg_row(False)
            else:
                msg_text += sm_peg_row(False)
            await msgs[i].edit(content=msg_text)
        else:
            header_text = ""
            for _ in range(outcomes):
                header_text += f"{nothing_emj}"
            header_text += f"{nothing_emj}\n"
            for _ in range(outcomes):
                header_text += f"{nothing_emj}"
            header_text += f"\n{wall_emj}{wall_emj}"
            for j in range(outcomes - 1):
                header_text += f"{letter_emjs[j]}{wall_emj}"
            header_text += f"{wall_emj}.\n"
            await msgs[0].edit(content=header_text)

        msg_text = empty_row(False)
        if lrg_row:
            space_num = int((current_column - 1) / 2)
            msg_text += lrg_peg_row(True)
        else:
            space_num = int(current_column / 2)
            msg_text += sm_peg_row(True)
        await msgs[i + 1].edit(content=msg_text)

        lrg_row = not lrg_row

    print(f"landing in: {current_column}")
    msg_text = empty_row(False)
    msg_text += sm_peg_row(False)
    await msgs[-2].edit(content=msg_text)

    selected_outcome = int(current_column / 2)
    outcomes_text = f"{wall_emj}"
    for i in range(outcomes):
        if i + 1 == selected_outcome:
            outcomes_text += f"{meatball_emj}{wall_emj}"
        else:
            outcomes_text += f"{slot_emj}{wall_emj}"
    outcomes_text += f"\n{nothing_emj}"
    for i in range(outcomes):
        outcomes_text += f"{number_emjs[i]}{nothing_emj}"
    outcomes_text += "."
    await msgs[-1].edit(content=outcomes_text)

    return selected_outcome


@bot.command()
async def plinko(ctx: Context):
    global is_active, outcomes, total_columns

    if is_active:
        await ctx.send(f"{ctx.author.mention} Plinko is already active.")
        return

    async def invalid_cmd():
        await ctx.send(f"{ctx.author.mention} Try **!plinko X**, where **X** is the number of outcomes (Min 2 - Max 20)")

    command_msg = ctx.message.content.split()
    if not len(command_msg) == 2:
        await invalid_cmd()
        return

    entered_number = command_msg[1].strip()
    if not entered_number.isdigit():
        await invalid_cmd()
        return

    outcomes = int(entered_number)
    if outcomes < MIN_OUTCOMES or outcomes > MAX_OUTCOMES:
        await invalid_cmd()
        return

    is_active = True
    total_columns = (outcomes * 2) + 1
    msgs = await print_board(ctx)

    start_at = 0
    while start_at == 0:
        reaction = (await bot.wait_for("reaction_add"))[0]
        if not reaction.message == msgs[-1] or reaction.count < 2:
            continue
        elif reaction.emoji.name == "Question":
            start_at = random.randint(1, outcomes - 1)
        else:
            start_at = ord(reaction.emoji.name.lower()[0]) - 96

    start_at = (start_at * 2) + 1
    await msgs[-1].clear_reactions()
    result = await drop_ball(msgs, start_at)

    final_msg = await ctx.send(f"{ctx.author.mention} The {meatball_emj} chose option **{result}**.\n"
                               f"The board will self-destruct in 5 seconds {bomb_emoji}")

    await asyncio.sleep(5)
    final_text = f"{ctx.author.mention} The {meatball_emj} chose option **{result}**."
    await final_msg.edit(content=final_text)
    for msg in msgs:
        await msg.delete()

    is_active = False


async def lite_print_board(ctx: Context) -> Message:
    global lite_msgs, lite_total_columns, lite_outcomes

    def empty_row() -> str:
        text = "|"
        for _ in range(lite_total_columns - 2):
            text += " "
        text += "|\n"
        return text

    def sm_peg_row() -> str:
        text = "| "
        for _ in range(lite_outcomes - 1):
            text += "^ "
        text += "|\n"
        return text

    def lrg_peg_row() -> str:
        text = "|"
        for _ in range(lite_outcomes - 1):
            text += "^ "
        text += "^|\n"
        return text

    lite_msgs = []

    header_text = "```"
    for _ in range(int((lite_total_columns - 1) / 2) - 1):
        header_text += " "
    header_text += "@\n\n--"
    for i in range(lite_outcomes - 1):
        header_text += f"{chr(ord('@') + (i + 1))}-"
    header_text += "-\n"
    lite_msgs.append(header_text)

    if (lite_outcomes % 2) == 0:
        num_peg_rows = lite_outcomes - 1
    else:
        num_peg_rows = lite_outcomes

    lrg_row = False
    for _ in range(num_peg_rows):
        msg_text = empty_row()
        if lrg_row:
            msg_text += lrg_peg_row()
        else:
            msg_text += sm_peg_row()
        lite_msgs.append(msg_text)
        lrg_row = not lrg_row

    outcomes_text = "|"
    for _ in range(lite_outcomes):
        outcomes_text += " |"
    outcomes_text += "\n "
    for i in range(lite_outcomes):
        outcomes_text += f"{(i + 1) if i < 9 else (i - 9) if i < 19 else i - 19} "
    outcomes_text += "```"
    lite_msgs.append(outcomes_text)

    final_text = ""
    for msg in lite_msgs:
        final_text += msg

    board_msg = await ctx.send(final_text)

    for i in range(lite_outcomes - 1):
        await board_msg.add_reaction(letter_emjs[i])
    await board_msg.add_reaction(question_mark_emj)

    return board_msg


async def lite_drop_ball(msg: Message, current_column: int) -> int:
    global lite_outcomes, lite_total_columns, lite_msgs

    def empty_row(meatball: bool) -> str:
        text = "|"
        if meatball:
            for j in range(lite_total_columns - 2):
                if j + 1 == current_column - 1:
                    text += "@"
                else:
                    text += " "
            text += "|\n"
        else:
            for _ in range(lite_total_columns - 2):
                text += " "
            text += "|\n"
        return text

    def sm_peg_row(meatball: bool) -> str:
        if meatball:
            text = "|"
            if space_num == 1:
                text += "@"
            else:
                text += " "
            for j in range(lite_outcomes - 1):
                if j + 1 == space_num - 1:
                    text += "^@"
                else:
                    text += "^ "
            text += "|\n"
        else:
            text = "| "
            for _ in range(lite_outcomes - 1):
                text += "^ "
            text += "|\n"
        return text

    def lrg_peg_row(meatball: bool) -> str:
        if meatball:
            text = "|"
            for k in range(lite_outcomes - 1):
                if k + 1 == space_num:
                    text += "^@"
                else:
                    text += "^ "
            text += "^|\n"
        else:
            text = "|"
            for _ in range(lite_outcomes - 1):
                text += "^ "
            text += "^|\n"
        return text

    print(f"starting column: {current_column}")

    header_text = "```\n"
    for _ in range(current_column - 1):
        header_text += " "
    header_text += "@\n--"
    for i in range(lite_outcomes - 1):
        header_text += f"{chr(ord('@') + (i + 1))}-"
    header_text += "-\n"
    lite_msgs[0] = header_text
    await lite_refresh(msg)

    await asyncio.sleep(1)

    header_text = "```\n\n--"
    for i in range(lite_outcomes - 1):
        if i + 1 == int((current_column - 1) / 2):
            header_text += "@-"
        else:
            header_text += f"{chr(ord('@') + (i + 1))}-"
    header_text += "-\n"
    lite_msgs[0] = header_text
    await lite_refresh(msg)

    await asyncio.sleep(1)

    lrg_row = False
    for i in range(len(lite_msgs) - 2):
        await asyncio.sleep(1)

        msg_text = empty_row(True)
        if current_column == 2:
            current_column += 1
        elif current_column == lite_outcomes * 2:
            current_column -= 1
        else:
            current_column += random.choice([-1, 1])
        print(f"moved to: {current_column}")

        if lrg_row:
            msg_text += lrg_peg_row(False)
        else:
            msg_text += sm_peg_row(False)
        lite_msgs[i + 1] = msg_text

        if i > 0:
            msg_text = empty_row(False)
            if not lrg_row:
                msg_text += lrg_peg_row(False)
            else:
                msg_text += sm_peg_row(False)
            lite_msgs[i] = msg_text
            await lite_refresh(msg)
        else:
            header_text = "```\n\n\n--"
            for j in range(lite_outcomes - 1):
                header_text += f"{chr(ord('@') + (j + 1))}-"
            header_text += "-\n"
            lite_msgs[0] = header_text
            await lite_refresh(msg)

        msg_text = empty_row(False)
        if lrg_row:
            space_num = int((current_column - 1) / 2)
            msg_text += lrg_peg_row(True)
        else:
            space_num = int(current_column / 2)
            msg_text += sm_peg_row(True)
        lite_msgs[i + 1] = msg_text
        await lite_refresh(msg)

        lrg_row = not lrg_row

    print(f"landing in: {current_column}")
    msg_text = empty_row(False)
    msg_text += sm_peg_row(False)
    lite_msgs[-2] = msg_text
    await lite_refresh(msg)

    selected_outcome = int(current_column / 2)
    outcomes_text = "|"
    for i in range(lite_outcomes):
        if i + 1 == selected_outcome:
            outcomes_text += "@|"
        else:
            outcomes_text += " |"
    outcomes_text += "\n "
    for i in range(lite_outcomes):
        outcomes_text += f"{(i + 1) if i < 9 else (i - 9) if i < 19 else i - 19} "
    outcomes_text += "```"
    lite_msgs[-1] = outcomes_text
    await lite_refresh(msg)

    return selected_outcome


async def lite_refresh(msg: Message):
    text = ""
    for row in lite_msgs:
        text += row
    await msg.edit(content=text)


@bot.command()
async def plinkolite(ctx: Context):
    global lite_is_active, lite_outcomes, lite_total_columns

    if lite_is_active:
        await ctx.send(f"{ctx.author.mention} Plinkolite is already active.")
        return

    async def invalid_cmd():
        await ctx.send(f"{ctx.author.mention} Try **!plinkolite X**, where **X** is the number of outcomes (Min 2 - Max 20)")

    command_msg = ctx.message.content.split()
    if not len(command_msg) == 2:
        await invalid_cmd()
        return

    entered_number = command_msg[1].strip()
    if not entered_number.isdigit():
        await invalid_cmd()
        return

    lite_outcomes = int(entered_number)
    if lite_outcomes < LITE_MIN_OUTCOMES or lite_outcomes > LITE_MAX_OUTCOMES:
        await invalid_cmd()
        return

    lite_is_active = True
    lite_total_columns = (lite_outcomes * 2) + 1
    msg = await lite_print_board(ctx)

    start_at = 0
    while start_at == 0:
        reaction = (await bot.wait_for("reaction_add"))[0]
        if not reaction.message == msg or reaction.count < 2:
            continue
        elif reaction.emoji.name == "Question":
            start_at = random.randint(1, lite_outcomes - 1)
        else:
            start_at = ord(reaction.emoji.name.lower()[0]) - 96

    start_at = (start_at * 2) + 1
    await msg.clear_reactions()
    result = await lite_drop_ball(msg, start_at)

    final_msg = await ctx.send(f"{ctx.author.mention} The {meatball_emj} chose option **{result}**.\n"
                               f"The board will self-destruct in 5 seconds {bomb_emoji}")

    await asyncio.sleep(5)
    final_text = f"{ctx.author.mention} The {meatball_emj} chose option **{result}**."
    await final_msg.edit(content=final_text)
    await msg.delete()

    lite_is_active = False
