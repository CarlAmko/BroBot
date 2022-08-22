import asyncio
import random
from typing import List, Dict
from enum import Enum

import emoji
from discord.ext.commands import Context
from discord import Message
from modules import bot
from modules.pets.data import db_pets
from modules.pets.data.models import Pet, StatusEffects

DUELING = 1011161175163142175

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

duel_is_active = False


class DuelType(Enum):
    ffa = 1
    team = 2


class Duel:
    wager: int
    turn: str


class PetInBattle:
    pet: Pet
    coords: [int] * 2
    status_effects: List[StatusEffects]
    initiative: int

    def __init__(self, new_pet: Pet):
        self.pet = new_pet


current_duel = Duel


async def print_battlefield(ctx: Context) -> List[Message]:
    messages = []
    battlefield = ""
    battlefield += nothing_emj
    for emj in letters_emjs:
        battlefield += emj
    messages.append(await ctx.send(f"{battlefield}"))
    for emj in number_emjs:
        battlefield = ""
        battlefield += emj
        for _ in range(10):
            battlefield += grid_emj
        messages.append(await ctx.send(f"{battlefield}"))
    return messages


async def add_to_battlefield(ctx: Context, messages: List[Message], pets: List[PetInBattle], duel_type: int):
    if duel_type == DuelType.ffa.value:
        starting_coords = [[0, 0], [0, 9], [9, 0], [9, 9]]
        if len(pets) == 2:
            pets[0].coords = starting_coords[0]
            pets[1].coords = starting_coords[3]
        else:
            for i in range(len(pets)):
                pets[i].coords = starting_coords[i]
    else:
        starting_coords = [[0, 3], [0, 6], [9, 3], [9, 6]]
        for i in range(len(pets)):
            pets[i].coords = starting_coords[i]

    await update_battlefield(ctx, messages, pets)


async def update_battlefield(ctx: Context, messages: List[Message], pets: List[PetInBattle]):
    for i in range(len(messages) - 1):
        pets_in_row = []
        for pet in pets:
            if pet.coords[0] == i:
                pets_in_row.append(pet)
        row_message = f"{number_emjs[i]}"
        for j in range(10):
            occupied = False
            for pet in pets_in_row:
                if pet.coords[1] == j:
                    row_message += emoji.emojize(pet.pet.pet_emoji)
                    occupied = True
            if not occupied:
                row_message += grid_emj
        await messages[i + 1].edit(content=row_message)


@bot.command()
async def duel(ctx: Context):
    global duel_is_active

    if not ctx.channel.id == DUELING:
        await ctx.send(f"{ctx.author.mention} Please only use **!duel** in <#{DUELING}>")
        return

    author = ctx.author
    author_id = author.id

    command_msg = ctx.message.content.split()
    if not len(command_msg) == 2:
        msg_to_delete = await ctx.send(f"{author.mention} Invalid !duel command. It should be !duel X (Where X is the "
                                       f"diggities you would like to wager on this duel.")
        await ctx.message.delete()
        return

    wager = int(command_msg[1].strip())
    await ctx.message.delete()
    if duel_is_active:
        return

    duel_is_active = True
    current_duel.wager = wager
    diggities = "diggity" if wager == 1 else "diggities"
    battlefield_messages = await print_battlefield(ctx)
    hosts_pet = db_pets.get_pet(author_id)
    pets_in_battle = [PetInBattle(hosts_pet)]
    duel_joined = False

    duel_join_msg = await ctx.send(f"{author.mention} has opened a duel for **{wager} {diggities}**!\n"
                                   f"Send \"**join**\" to request to join the duel.\n"
                                   f"Duel shall commence in 1 minute.")
    duel_setup_text = duel_join_msg.content

    cannot_join = [author_id]
    duelists = []
    while len(pets_in_battle) < 4:
        try:
            reply = await bot.wait_for('message', timeout=60.0)
        except asyncio.TimeoutError:
            if not duel_joined:
                no_one_dueling_msg = await ctx.send(f"{author.mention} Seems like no one was willing to duel. "
                                                    f"Try again later.")
                return
            else:
                await duel_join_msg.edit(content=f"Duel is about to begin {loading_emj}")
                break
        else:
            if reply.content.lower() == "join" and reply.author.id not in cannot_join:
                if not db_pets.check_pet(reply.author.id):
                    no_pet_msg = await ctx.send(f"{reply.author.mention} You do not have a pet.")
                    continue

                request_msg = await ctx.send(f"{author.mention}\n{reply.author.mention} would like to join the "
                                             f"duel.\nSend \"**accept**\" to accept them. "
                                             f"\"**decline**\" to decline them.")
                host_responded = False
                while not host_responded:
                    try:
                        host_reply = await bot.wait_for('message', timeout=60.0)
                    except asyncio.TimeoutError:
                        host_not_accept_msg = await ctx.send(f"{reply.author.mention}\n"
                                                             f"{author.mention} did not accept.")
                        break
                    else:
                        if host_reply.author.id == ctx.author.id:
                            if host_reply.content.lower() == "accept":
                                host_responded = True
                                cannot_join.append(reply.author.id)
                                duel_joined = True
                                joiners_pet = db_pets.get_pet(reply.author.id)
                                pets_in_battle.append(PetInBattle(joiners_pet))
                                duelists.append(reply.author)
                                new_msg_text = duel_setup_text + f"\n{reply.author.mention} has joined the duel."
                                await duel_join_msg.edit(content=(new_msg_text + f"\nSend \"**start**\" to start the "
                                                                                 f"duel now."))
                                await request_msg.delete()
                            elif host_reply.content.lower() == "decline":
                                host_responded = True
                                cannot_join.append(reply.author.id)
                                await request_msg.delete()
                        if reply.channel.id == DUELING:
                            await host_reply.delete()
            elif reply.content.lower() == "start" and reply.author.id == author_id:
                await duel_join_msg.edit(content=f"Duel is about to begin {loading_emj}")
                break
            if reply.channel.id == DUELING:
                await reply.delete()

    await duel_join_msg.delete()

    if len(pets_in_battle) > 2:
        duel_type = 0
        duel_type_msg = await ctx.send(f"{author.mention}\n"
                                       f"Send \"ffa\" for a free-for-all duel or \"team\" for a team duel.")
        while duel_type == 0:
            try:
                reply = await bot.wait_for('message', timeout=60.0)
            except asyncio.TimeoutError:
                type_not_selected_msg = await ctx.send(f"{author.mention} You didn't select a duel type in time. "
                                                       f"Duel cancelled.")
                return
            else:
                if reply.author.id == author_id:
                    if reply.content.lower() == "ffa":
                        duel_type = DuelType.ffa.value
                    elif reply.content.lower() == "team":
                        duel_type = DuelType.team.value
                if reply.channel.id == DUELING:
                    await reply.delete()
        await duel_type_msg.delete()
    else:
        duel_type = DuelType.ffa.value

    if duel_type == DuelType.team.value:
        team_select_text = f"{author.mention}, enter the number of user you want to team with or send \"random\"\n"
        for i in range(len(duelists)):
            team_select_text += f"**{i + 1}:** {duelists[i].mention}\n"
        team_select_text += "You have 30 seconds to select or else it will be random."
        team_select_msg = await ctx.send(team_select_text)

        host_teammate = 0
        while host_teammate == 0:
            try:
                reply = await bot.wait_for('message', timeout=30.0)
            except asyncio.TimeoutError:
                type_not_selected_msg = await ctx.send(f"{author.mention} Times Up!")
                host_teammate = random.randint(1, len(duelists))
                return
            else:
                if reply.author.id == author_id:
                    if reply.content == "1":
                        host_teammate = 1
                    elif reply.content == "2":
                        host_teammate = 2
                    elif reply.content == "3":
                        if not len(duelists) > 3:
                            continue
                        host_teammate = 3
                if reply.channel.id == DUELING:
                    await reply.delete()

        if not host_teammate == 1:
            pets_in_battle[1], pets_in_battle[host_teammate] = pets_in_battle[host_teammate], pets_in_battle[1]

    history = await bot.get_channel(ctx.channel.id).history(limit=None).flatten()
    for msg in history:
        if msg not in battlefield_messages:
            await msg.delete()

    await add_to_battlefield(ctx, battlefield_messages, pets_in_battle, duel_type)

    # TODO Remove this
    final_msg = await ctx.send("Dueling is under construction. This channel will empty itself in 30 seconds.")
    await asyncio.sleep(30)
    await final_msg.delete()
    for msg in battlefield_messages:
        await msg.delete()

    duel_is_active = False
