import asyncio
import random
import time
from typing import List, Dict
from enum import Enum

import discord
import emoji
from discord.ext.commands import Context
from discord import Message, Member, TextChannel
from discord.utils import get
from modules import bot
from modules.pets.data import db_pets
from modules.pets.data.models import Pet, StatusEffects, Stats, BASE_MOVEMENT

PETS_CATEGORY = 1011160840201850970
BATTLEFIELD_SIZE = 10
ROWS_PER_MESSAGE = 5
COLUMN_LETTERS = 'abcdefghij'
ROW_NUMBERS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
FFA_STARTING_COORDS = [[0, 0], [0, 9], [9, 0], [9, 9]]
TEAM_STARTING_COORDS = [[0, 3], [0, 6], [9, 3], [9, 6]]

nothing_emj = emoji.emojize("<:nothing:1004150080779059381>")
grid_emj = emoji.emojize("<:Grid:1009500126177407016>")
loading_emj = emoji.emojize("<a:loading:734622445910360105>")
bomb_emj = emoji.emojize(":bomb:")
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
    teams = 2


class DuelingPet:
    pet: Pet
    owner: Member
    location: List[int]
    initiative: int

    def __init__(self, owner: Member):
        self.pet = db_pets.get_pet(owner.id)
        self.owner = owner
        self.location = []
        self.initiative = random.randint(1, 20) + self.pet.pet_stats[Stats.ins.value]


class Duel:
    is_active: bool
    can_start: bool
    can_join: bool
    has_started: bool
    channel: TextChannel
    wager: int
    ctx: Context
    pets: List[DuelingPet]

    def __init__(self, new_channel: TextChannel, ctx: Context):
        self.is_active = True
        self.can_start = False
        self.can_join = False
        self.has_started = False
        self.channel = new_channel
        self.wager = 0
        self.ctx = ctx
        self.pets = [DuelingPet(ctx.author)]


duels: Dict[Member, Duel] = {}
joiners: List[Member] = []
declined: List[Member] = []

new_duel_msg: Message
host_greeting_msg: Message


async def has_duel(ctx: Context) -> bool:
    global duels, host_greeting_msg

    host = ctx.author

    if host in duels and duels[host].is_active:
        await ctx.send(f"{host.mention} You have an active duel already.\n<#{duels[host].channel.id}>")
        return True
    else:
        pet_category = get(ctx.guild.categories, id=PETS_CATEGORY)

        channel_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            host: discord.PermissionOverwrite(read_messages=True)
        }

        new_channel = await ctx.guild.create_text_channel(
            name=f"{ctx.author.nick}'s duel",
            overwrites=channel_overwrites,
            category=pet_category
        )

        duels[host] = Duel(new_channel, ctx)
        host_greeting_msg = await duels[host].channel.send(f"{host.mention} Welcome to your dueling channel.")
        return False


async def close_duel(ctx: Context):
    global duels

    host = ctx.author

    await duels[host].channel.send("This channel will self-destruct in 1 minute.")
    await duels[host].channel.send(f"{bomb_emj}")
    await asyncio.sleep(60)
    await duels[host].channel.delete()
    duels[host].is_active = False


async def join_process(ctx: Context):
    global duels, host_greeting_msg

    host = ctx.author
    current_duel = duels[host]

    current_duel.can_join = True

    while not current_duel.has_started:
        if len(current_duel.pets) == 4:
            current_duel.can_join = False

        if len(current_duel.pets) > 1 and not current_duel.can_start:
            current_duel.can_start = True
            host_greeting_text = host_greeting_msg.content + f"\nSend \"**!start**\" start the duel now."
            await host_greeting_msg.edit(content=host_greeting_text)

        await asyncio.sleep(1)


@bot.command()
async def duel(ctx: Context):
    global duels, new_duel_msg, host_greeting_msg

    host = ctx.author
    host_id = host.id

    if not db_pets.check_pet(host.id):
        await ctx.send(f"{host.mention} You do not have a pet. Use \"**!newpet**\" to get one.")
        return

    if await has_duel(ctx):
        return

    current_duel = duels[host]
    duel_channel = current_duel.channel

    command_msg = ctx.message.content.split()

    if len(command_msg) == 1:
        current_duel.wager = 0

    else:
        wager: str = command_msg[1].strip()

        if not wager.isdigit():
            await duel_channel.send(f"{host.mention} Your wager was invalid.")
            await close_duel(ctx)
            return

        current_duel.wager = int(wager)

    diggity_text = "diggity" if current_duel.wager == 1 else "diggities"

    new_duel_text = f"{host.mention} has opened a duel for **{current_duel.wager} {diggity_text}**!\n" \
                    f"Send \"**!join {host.mention}**\" to request to join the duel."
    new_duel_msg = await ctx.send(new_duel_text)

    await join_process(ctx)
    await current_duel.channel.purge()



    await close_duel(ctx)


@bot.command()
async def join(ctx: Context):
    global duels, joiners, declined, new_duel_msg

    joiner = ctx.author

    if not db_pets.check_pet(joiner.id):
        await ctx.send(f"{joiner.mention} You do not have a pet. Use \"**!newpet**\" to get one.")
        return

    if not len(ctx.message.mentions) > 0:
        await ctx.send(f"{joiner.mention} You need to mention the host who's duel you would like to join.")
        return

    host = ctx.message.mentions[0]

    if joiner.id == host.id:
        await ctx.send(f"{joiner.mention} You can't join your own duel.")
        return

    if joiner in declined:
        await ctx.send(f"{joiner.mention} **{host.nick}** has declined your request. You cannot join.")

    if host not in duels:
        await ctx.send(f"{joiner.mention} **{host.nick}** isn't hosting a duel.")
        return

    joined_duel = duels[host]

    if joined_duel.has_started:
        await ctx.send(f"{joiner.mention} **{host.nick}'s** duel already began.")
        return

    joiners.append(joiner)
    await joined_duel.channel.send(f"{host.mention}\n"
                                   f"**{joiner.nick}** has requested to join your duel.\n"
                                   f"Send \"**!accept {joiner.mention}**\" to accept their request.\n"
                                   f"Send \"**!decline {joiner.mention}**\" to decline their request.")

    while joiner in joiners and not joined_duel.has_started:
        await asyncio.sleep(1)

    if joiner in joiners or joiner in declined:
        await ctx.send(f"{joiner.mention} **{host.nick}** did not accept.\n"
                       f"Send \"**!spectate {host.mention}**\" to watch the duel.")
        return

    joined_duel.pets.append(DuelingPet(joiner))
    await joined_duel.channel.set_permissions(joiner, read_messages=True)

    new_duel_text = new_duel_msg.content + f"\n**{joiner.nick}** has joined the duel!"
    await new_duel_msg.edit(content=new_duel_text)


@bot.command()
async def accept(ctx: Context):
    global duels, joiners

    host = ctx.author
    host_duel = duels[host]

    if not len(ctx.message.mentions) > 0:
        await ctx.send(f"{host.mention} You need to mention the user your want to accept.")
        return

    joiner = ctx.message.mentions[0]

    if host not in duels or not host_duel.is_active:
        await ctx.send(f"{host.mention} You are not hosting a duel.")
        return

    if host_duel.has_started:
        await ctx.send(f"{host.mention} Your duel has already started.")
        return

    if joiner not in joiners:
        await ctx.send(f"{host.mention} **{joiner.nick}** has not requested to join your duel.")
        return

    for user in joiners:
        if user.id == joiner.id:
            joiners.remove(user)


@bot.command()
async def decline(ctx: Context):
    global duels, joiners, declined

    host = ctx.author
    host_duel = duels[host]

    if not len(ctx.message.mentions) > 0:
        await ctx.send(f"{host.mention} You need to mention the user your want to accept.")
        return

    joiner = ctx.message.mentions[0]

    if host not in duels or not host_duel.is_active:
        await ctx.send(f"{host.mention} You are not hosting a duel.")
        return

    if host_duel.has_started:
        await ctx.send(f"{host.mention} Your duel has already started.")
        return

    if joiner not in joiners:
        await ctx.send(f"{host.mention} **{joiner.nick}** has not requested to join your duel.")
        return

    for user in joiners:
        if user.id == joiner.id:
            joiners.remove(user)
            declined.append(user)


@bot.command()
async def spectate(ctx: Context):
    global duels, new_duel_msg

    spectator = ctx.author

    if not len(ctx.message.mentions) > 0:
        await ctx.send(f"{spectator.mention} You need to mention the host who's duel you would like to watch.")
        return

    host = ctx.message.mentions[0]
    host_duel = duels[host]

    if spectator.id == host.id:
        await ctx.send(f"{spectator.mention} It is your duel...")
        return

    if host not in duels:
        await ctx.send(f"{spectator.mention} **{host.nick}** isn't hosting a duel.")
        return

    await host_duel.channel.set_permissions(spectator, read_messages=True, send_messages=False)

    new_duel_text = new_duel_msg.content + f"\n**{spectator.nick}** is watching the duel."
    await new_duel_msg.edit(content=new_duel_text)


@bot.command()
async def start(ctx: Context):
    global duels, new_duel_msg

    host = ctx.author
    host_duel = duels[host]

    if host not in duels or not host_duel.is_active:
        await ctx.send(f"{host.mention} You are not hosting a duel.")
        return

    if host_duel.has_started:
        await ctx.send(f"{host.mention} Your duel has already started.")
        return

    if not host_duel.can_start:
        await ctx.send(f"{host.mention} No one has joined your duel yet.")
        return

    host_duel.can_join = False

    new_duel_text = new_duel_msg.content + f"The duel has started.\n" \
                                           f"Send \"**!spectate {host.mention}**\" to watch the duel."

    host_duel.has_started = True
