import asyncio
import random
from typing import Dict

from modules import bot
import emoji
from discord import Message, Emoji
from discord.utils import get
from discord.ext.commands import Context

COOLDOWN = 60
EXPIRE_TIME = 10
SAVE_ID = 799067451786264616

save_react = emoji.emojize('<:POG:799067451786264616>')

names = [
    "Tim",
    "Joe",
    "Spencer",
    "Sarah",
    "Evan",
    "Johnny",
    "Jacob",
    "Kevin",
    "Tabitha",
    "Pierce",
    "Jess",
    "Ginger",
    "Matt",
    "Carl",
    "Emily",
    "Ember",
    "John",
    "Shae"
]

sucka = ["sucka"]

pets = [
    "Meeko",
    "Buster",
    "Nell",
    "Nova",
    "Aurora",
    "Houdini",
    "Erwin"
]

not_safe_prewords = [
    "Hate",
    "Fuck",
    "Sniff",
    "Duck"
]

safe_prewords = [
    "Love",
    "Fish",
    "Boogie",
    "Kiss",
    "Hug",
    "Poke",
    "Miss",
    "Pet"
]

doing_things = [
    "playing hunt",
    "hugging",
    "eating out of the jif jar",
    "sneaking into the jif cinema",
    "sizzling",
    "in the game bath",
    "fighting in the KFC parking lot",
    "buttering bugs",
    "gas lighting",
    "girl bossing",
    "quoting",
    "victim blaming",
    "gas blaming",
    "victim lighting",
    "explaining Heathcliff comics",
    "disrespecting the meatball",
    "eating Little Caesar's",
    "fishing in the cord",
    "hittin the slots",
    "pulling the car around",
    "advising their clients",
    "playing Jessbox",
    "getting rich",
    "reviewing the feet pic tourney",
    "on COD mobile",
    "baking as cake",
    "makina a pizza a piea",
    "deleting the evidence",
    "stylen on eachother",
    "ganking mid",
    "studying for the quote quiz",
    "making a Caerleon run",
    "changing their nicknames"
]

cooldowns: Dict[str, bool] = {}


async def cooldown(msg: Message, key: str):
    await asyncio.sleep(COOLDOWN)
    cooldowns[key] = False


async def expire_msg(msg: Message):
    await asyncio.sleep(EXPIRE_TIME)
    await msg.delete()


def safe_for_pets(word: str) -> bool:
    if word in safe_prewords:
        return True
    return False


@bot.command()
async def tellem(ctx: Context):

    await ctx.message.delete()

    if 'tellem' in cooldowns and cooldowns['tellem']:
        msg = await ctx.send(f"{ctx.author.mention} That command is on cooldown.")
        await expire_msg(msg)
        return

    cooldowns['tellem'] = True
    text = random.choice(safe_prewords + not_safe_prewords) + " you "

    if text == "Duck":
        name = random.choice(names + sucka)
    elif safe_for_pets(text):
        name = random.choice(names + pets)
    else:
        name = random.choice(names)

    text += name + "."
    msg = await ctx.send(text, tts=True)
    await cooldown(msg, 'tellem')


@bot.command()
async def wuhhapa(ctx: Context):

    await ctx.message.delete()

    if 'wuhhapa' in cooldowns and cooldowns['wuhhapa']:
        msg = await ctx.send(f"{ctx.author.mention} That command is on cooldown.")
        await expire_msg(msg)
        return

    cooldowns['wuhhapa'] = True
    name_1 = random.choice(names + pets)
    name_2 = random.choice(names + pets)
    while name_2 == name_1:
        name_2 = random.choice(names + pets)

    text = "I saw " + name_1 + " and " + name_2 + " " + random.choice(doing_things) + "."

    msg = await ctx.send(text, tts=True)
    await cooldown(msg, 'wuhhapa')


@bot.command()
async def votebb(ctx: Context):
    await ctx.message.delete()
    await ctx.send("As your mayor I will abolish Tim.", tts=True)
