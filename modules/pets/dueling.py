import asyncio
import random
import time
from typing import List, Dict
from enum import Enum

import emoji
from discord.ext.commands import Context
from discord import Message, Member
from modules import bot
from modules.pets.data import db_pets
from modules.pets.data.models import Pet, StatusEffects, Stats

DUELING = 1011161175163142175
BATTLEFIELD_SIZE = 10
ROWS_PER_MESSAGE = 5
COLUMN_LETTERS = 'abcdefghij'
ROW_NUMBERS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
FFA_STARTING_COORDS = [[0, 0], [0, 9], [9, 0], [9, 9]]
TEAM_STARTING_COORDS = [[0, 3], [0, 6], [9, 3], [9, 6]]

nothing_emj = emoji.emojize("<:nothing:1004150080779059381>")
grid_emj = emoji.emojize("<:Grid:1009500126177407016>")
loading_emj = emoji.emojize("<a:loading:734622445910360105>")
letters_emjs = [
        emoji.emojize('<:A_:1009500338895732746>'),
        emoji.emojize('<:B_:1009502153980780645>'),
        emoji.emojize('<:C_:1009502173719179275>'),
        emoji.emojize('<:D_:1009502196926255104>'),
        emoji.emojize('<:E_:1009502216882765924>'),
        emoji.emojize('<:F_:1009503764429934632>'),
        emoji.emojize('<:G_:1009502265725431901>'),
        emoji.emojize('<:H_:1009502284989866105>'),
        emoji.emojize('<:I_:1009502306200473664>'),
        emoji.emojize('<:J_:1009502323405496396>')
]
number_emjs = [
    emoji.emojize('<:1_:1009502340346290206>'),
    emoji.emojize('<:2_:1009502356595019857>'),
    emoji.emojize('<:3_:1009502371447058442>'),
    emoji.emojize('<:4_:1009502388979257456>'),
    emoji.emojize('<:5_:1009502405873913926>'),
    emoji.emojize('<:6_:1009502421799678005>'),
    emoji.emojize('<:7_:1009502440229449839>'),
    emoji.emojize('<:8_:1009502456255877140>'),
    emoji.emojize('<:9_:1009502471594463352>'),
    emoji.emojize('<:10:1009502487042072696>')
]


class DuelType(Enum):
    ffa = 1
    team = 2


class PetInDuel:
    pet: Pet
    owner: Member
    coords: [int] * 2
    status_effects: List[StatusEffects]
    initiative: int
    is_turn: bool
    remaining_movement: int

    def __init__(self, new_pet: Pet, current_owner: Member):
        self.pet = new_pet
        self.owner = current_owner
        self.initiative = random.randint(1, 20) + new_pet.pet_stats[Stats.ins.value]


class Duel:
    duel_context: Context
    is_active = False
    pets: List[PetInDuel]
    battlefield: List[Message]
    wager: int
    type: int
    round: int
    turn_order: List[PetInDuel]
    occupied_spaces: List[([int] * 2)]


class Turn:
    pet: PetInDuel
    used_action: bool


current_duel = Duel


async def set_starting_positions():
    global current_duel

    if current_duel.type == DuelType.ffa.value:
        if len(current_duel.pets) == 2:
            current_duel.pets[0].coords = FFA_STARTING_COORDS[0]
            current_duel.occupied_spaces.append(FFA_STARTING_COORDS[0])
            current_duel.pets[1].coords = FFA_STARTING_COORDS[3]
            current_duel.occupied_spaces.append(FFA_STARTING_COORDS[3])
        else:
            for i in range(len(current_duel.pets)):
                current_duel.pets[i].coords = FFA_STARTING_COORDS[i]
                current_duel.occupied_spaces.append(FFA_STARTING_COORDS[i])
    else:
        for i in range(len(current_duel.pets)):
            current_duel.pets[i].coords = TEAM_STARTING_COORDS[i]
            current_duel.occupied_spaces.append(TEAM_STARTING_COORDS[i])


async def setup_battlefield():
    global current_duel

    current_duel.battlefield = []
    if len(current_duel.battlefield) == 0:
        header = ""
        if current_duel.type == DuelType.ffa.value:
            header += "Free-for-all duel with:  "
            for pet in current_duel.pets:
                header += f"{pet.owner.mention}  "
        else:
            header += "Team duel with: "
            for i in range(2):
                header += f"{current_duel.pets[i].owner.mention}  "
            header += "VS  "
            for i in range(2, len(current_duel.pets)):
                header += f"{current_duel.pets[i].owner.mention}  "

        header += f"\n\n{nothing_emj}"
        for emj in letters_emjs:
            header += emj
        current_duel.battlefield.append(await current_duel.duel_context.send(header))

    await update_battlefield()


async def update_battlefield():
    global current_duel

    for i in range(2):
        row_messages = ""
        for j in range(ROWS_PER_MESSAGE):
            pets_in_row = []
            for pet in current_duel.pets:
                if pet.coords[0] == j + (ROWS_PER_MESSAGE * i):
                    pets_in_row.append(pet)
            row_messages += f"{number_emjs[j + (ROWS_PER_MESSAGE * i)]}"
            for k in range(10):
                occupied = False
                for pet in pets_in_row:
                    if pet.coords[1] == k:
                        row_messages += emoji.emojize(pet.pet.pet_emoji)
                        occupied = True
                if not occupied:
                    row_messages += grid_emj
            row_messages += "\n"

        if len(current_duel.battlefield) <= 2:
            current_duel.battlefield.append(await current_duel.duel_context.send(row_messages))
        else:
            await current_duel.battlefield[i + 1].edit(content=row_messages)


async def start_duel():
    global current_duel

    build_turn_order()
    while current_duel.is_active:
        turn_index = 0

        for pet_turn in current_duel.turn_order:
            pet_turn.is_turn = True
            turn_order_msg = await current_duel.duel_context.send(f"{nothing_emj}\n"
                                                                  f"It is **{pet_turn.owner.mention}'s** turn.")

            turn_msg = await current_duel.duel_context.send(f"{nothing_emj}\n"
                                                            f"{nothing_emj}{nothing_emj}{nothing_emj}{nothing_emj}"
                                                            f"{nothing_emj}{nothing_emj}"
                                                            f"**ACTIONS**\nAttack  |  Move  |  Skill  |  Item  "
                                                            f"|  End Turn  |  Surrender")

            while pet_turn.is_turn:

                try:
                    reply = await bot.wait_for('message', timeout=600.0)

                except asyncio.TimeoutError:
                    pet_turn.is_turn = False

                else:
                    if reply.author.id == pet_turn.owner.id:
                        response = reply.content.lower()

                        if response == "move":
                            is_moving = True
                            move_msg = await current_duel.duel_context.send("Where would you like to move? "
                                                                            "(Format: \"**A 1**\". A is the column "
                                                                            "letter and 1 is the row number.)")
                            while is_moving:
                                try:
                                    move_reply = await bot.wait_for('message', timeout=60.0)

                                except asyncio.TimeoutError:
                                    is_moving = False

                                else:
                                    if move_reply.author.id == pet_turn.owner.id:
                                        move_response = move_reply.content.lower()

                                        # TODO input security
                                        move_to = move_response.split()
                                        if len(move_to) == 2:
                                            if move_to[0] in COLUMN_LETTERS and move_to[1] in ROW_NUMBERS:
                                                pet_turn.coords[0] = int(move_to[1]) - 1
                                                pet_turn.coords[1] = COLUMN_LETTERS.find(move_to[0])
                                                is_moving = False

                                    await delete_reply(move_reply)

                            await move_msg.delete()
                        # End of: if response == "move"

                        elif response == "surrender":
                            remove_from_duel(int(pet_turn.owner.id), turn_index)
                            break

                        elif response == "end turn":
                            pet_turn.is_turn = False
                    # End of: if reply.author.id == pet_turn.owner.id

                    await delete_reply(reply)
                    await update_battlefield()
                # End of: try for action
            # End of: while pet_turn.is_turn

            await turn_order_msg.delete()
            await turn_msg.delete()
            turn_index += 1

        # End of: for pet_turn in current_duel.turn_order

        if len(current_duel.turn_order) < 2:
            winner = current_duel.turn_order[0]
            await current_duel.duel_context.send(f"{winner.owner.mention} and **{winner.pet.name}** "
                                                 f"{emoji.emojize(winner.pet.pet_emoji)} have won the duel!")
            current_duel.is_active = False
            return

        await update_battlefield()

    # End of: while current_duel.is_active


def build_turn_order():
    global current_duel

    current_duel.turn_order = []
    for i in range(len(current_duel.pets)):
        current_duel.turn_order.append(current_duel.pets[i])

    current_duel.turn_order.sort(key=lambda x: x.initiative)


def remove_from_duel(pet: int, turn_index: int):
    global current_duel

    for i in range(len(current_duel.pets)):
        if pet == int(current_duel.pets[i].owner.id):
            del current_duel.pets[i]

    del current_duel.turn_order[turn_index]


async def delete_reply(reply: Message):
    if reply.channel.id == DUELING:
        await reply.delete()


# Command to start a new duel
@bot.command()
async def duel(ctx: Context):
    global current_duel

    # Makes sure that the duel command is being called in #dueling_only
    if not ctx.channel.id == DUELING:
        await ctx.send(f"{ctx.author.mention} Please only use **!duel** in <#{DUELING}>")
        return

    # If duel is already active ignore !duel commands
    if current_duel.is_active:
        await ctx.message.delete()
        return

    # Store command callers info
    author = ctx.author
    author_id = author.id

    # Split command message to grab wager amount
    command_msg = ctx.message.content.split()
    if not len(command_msg) == 2:
        msg_to_delete = await ctx.send(f"{author.mention} Invalid !duel command. It should be !duel X (Where X is the "
                                       f"diggities you would like to wager on this duel.")
        await ctx.message.delete()
        return

    # Grab wager
    wager = int(command_msg[1].strip())

    # In new duel: Store context, set as active, store wager
    current_duel.duel_context = ctx
    current_duel.is_active = True
    current_duel.wager = wager

    # Delete calling message
    await ctx.message.delete()

    # Store host's pet as a dueling pet
    current_duel.pets = [PetInDuel(db_pets.get_pet(author_id), author)]

    # Use singular form of digities for 1 in wager
    diggities = "diggity" if wager == 1 else "diggities"

    # Output new active duel message and store the contents
    duel_join_msg = await ctx.send(f"{author.mention} has opened a duel for **{wager} {diggities}**!\n"
                                   f"Send \"**join**\" to request to join the duel.\n"
                                   f"Duel shall commence in 1 minute.")
    duel_setup_text = duel_join_msg.content

    # Start duel joined flag and list of players who cannot join the current duel
    duel_joined = False
    cannot_join = [author_id]

    # Loop until there are 4 pets in the duel (Is broken out of if host chooses to start with less)
    while len(current_duel.pets) < 4:

        # Wait for join message to come in
        try:
            reply = await bot.wait_for('message', timeout=60.0)

        # New duel timed out with no new joiners
        except asyncio.TimeoutError:
            if not duel_joined:
                no_one_dueling_msg = await ctx.send(f"{author.mention} Seems like no one was willing to duel. "
                                                    f"Try again later.")
                return
            else:
                await duel_join_msg.edit(content=f"Duel is about to begin {loading_emj}")
                break

        else:
            # Check if the response message was "join" and that the sender is allowed to join
            if reply.content.lower() == "join" and reply.author.id not in cannot_join:

                # Checks that the joiner has a pet
                if not db_pets.check_pet(reply.author.id):
                    no_pet_msg = await ctx.send(f"{reply.author.mention} You do not have a pet.")
                    continue

                # Informs the host that someone is attempting to join and prompts them to accept or decline
                request_msg = await ctx.send(f"{author.mention}\n**{reply.author.mention}** would like to join the "
                                             f"duel.\nSend \"**accept**\" to accept them. "
                                             f"\"**decline**\" to decline them.")
                # Flag for whether the host replies to join request
                host_responded = False

                # Loop while host has not sent a valid response and request has not timed out
                while not host_responded:

                    # Wait for host to reply to join request
                    try:
                        host_reply = await bot.wait_for('message', timeout=60.0)

                    # Join request timed out without host response
                    except asyncio.TimeoutError:
                        host_not_accept_msg = await ctx.send(f"{reply.author.mention}\n"
                                                             f"**{author.nick}** did not accept.")
                        break

                    else:
                        # Ensures the response to the join request is coming from the host
                        if host_reply.author.id == ctx.author.id:

                            # Host accepts the join request
                            if host_reply.content.lower() == "accept":
                                host_responded = True
                                cannot_join.append(reply.author.id)
                                joiners_pet = db_pets.get_pet(reply.author.id)
                                current_duel.pets.append(PetInDuel(joiners_pet, reply.author))

                                # Case where the joiner is the first joiner (Message formatting)
                                if not duel_joined:
                                    duel_setup_text += "\n"

                                # Flag duel as joined and update message to show that the joiner is in the duel
                                duel_joined = True
                                duel_setup_text += f"\n**{reply.author.mention}** has joined the duel."
                                await duel_join_msg.edit(content=(duel_setup_text + f"\n\nSend \"**start**\" to start "
                                                                                    f"the duel now."))
                                await request_msg.delete()

                            # Host declines the join request
                            elif host_reply.content.lower() == "decline":
                                host_responded = True
                                cannot_join.append(reply.author.id)
                                await request_msg.delete()

                        # Prevents bot from deleting messages in other channels while waiting for responses
                        await delete_reply(host_reply)

            # Once duel is joined allow only host to start duel with current joiners
            elif duel_joined and reply.content.lower() == "start" and reply.author.id == author_id:
                await duel_join_msg.edit(content=f"Duel is about to begin {loading_emj}")
                break

            await delete_reply(reply)

    # Delete new duel info message before outputting battlefield
    await duel_join_msg.delete()

    # If more than 1 joiner allow host to select free-for-all or teams
    if len(current_duel.pets) > 2:

        # Set type to 0 to state that the type has not been selected
        current_duel.type = 0
        duel_type_msg = await ctx.send(f"{author.mention}\n"
                                       f"Send \"ffa\" for a free-for-all duel or \"team\" for a team duel.")

        # Loop while a type has not been selected
        while current_duel.type == 0:

            # Wait for host to choose duel type
            try:
                reply = await bot.wait_for('message', timeout=60.0)

            # Mode select timed out and duel is cancelled
            except asyncio.TimeoutError:
                type_not_selected_msg = await ctx.send(f"{author.mention} You didn't select a duel type in time. "
                                                       f"Duel cancelled.")
                return

            else:
                # Only host may choose mode
                if reply.author.id == author_id:

                    # Chose free-for-all
                    if reply.content.lower() == "ffa":
                        current_duel.type = DuelType.ffa.value

                    # Chose teams
                    elif reply.content.lower() == "team":
                        current_duel.type = DuelType.team.value

                await delete_reply(reply)

        # Delete mode select message before outputting battlefield
        await duel_type_msg.delete()

    # Only 1 joiner so free-for-all
    else:
        current_duel.type = DuelType.ffa.value

    # If teams allow host to choose their teammate
    if current_duel.type == DuelType.team.value:
        team_select_text = f"{author.mention}, enter the number of user you want to team with or send \"random\"\n"
        for i in range(len(current_duel.pets) - 1):
            team_select_text += f"**{i + 1}:** {current_duel.pets[i + 1].owner.nick}\n"
        team_select_text += "You have 30 seconds to select or else it will be random."
        team_select_msg = await ctx.send(team_select_text)

        host_teammate = -1

        # Loop while host has not entered a valid teammate selection
        while host_teammate == -1:

            # Wait for teammate selection
            try:
                reply = await bot.wait_for('message', timeout=30.0)

            # Teammate select timed out and a random teammate was assigned
            except asyncio.TimeoutError:
                type_not_selected_msg = await ctx.send(f"{author.mention} Times Up!")
                host_teammate = random.randint(1, len(current_duel.pets) - 1)

            else:
                # Only host may choose their teammate
                if reply.author.id == author_id:
                    if reply.content == "1":
                        host_teammate = 1
                    elif reply.content == "2":
                        host_teammate = 2
                    elif reply.content == "3":
                        if not (len(current_duel.pets) - 1) > 3:
                            continue
                        host_teammate = 3

                    # Random teammate selected
                    elif reply.content == "random":
                        host_teammate = random.randint(1, len(current_duel.pets) - 1)

                await delete_reply(reply)

        # If the host didn't select the first joiner then rearrange pets in duel accordingly
        if not host_teammate == 1:
            current_duel.pets[1], current_duel.pets[host_teammate] = current_duel.pets[host_teammate], current_duel.pets[1]

    # Clear channel of all messages before outputting battlefield
    history = await bot.get_channel(ctx.channel.id).history(limit=None).flatten()
    for msg in history:
        await msg.delete()

    # Duel begins

    await set_starting_positions()
    await setup_battlefield()
    await start_duel()

    current_duel = Duel
