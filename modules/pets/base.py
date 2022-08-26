import asyncio

from discord.ext.commands import Context
from database.db import update_currency, get_currency
from modules import bot
from discord import Message
from modules.pets.data.models import Pet, Stats
from modules.pets.data import db_pets
import emoji
from env import ADMIN_IDS

PET_GENERAL = 1010952816908574750
PET_REROLLS = 4

nothing_emj = emoji.emojize("<:nothing:1004150080779059381>")


async def print_pet_info(ctx: Context, current_pet: Pet) -> Message:
    pet_data_msg = await ctx.send(f"{ctx.author.mention} {emoji.emojize(current_pet.pet_emoji)}\n"
                                  f"**Name: **{current_pet.name}\n"
                                  f"**Level: **{current_pet.level}\n"
                                  f"**XP: **{current_pet.xp}\n"
                                  f"**HP: **{current_pet.current_hp} / {current_pet.max_hp}\n"
                                  f"\n"
                                  f"**Might: **{current_pet.pet_stats[Stats.mgt.value]}\n"
                                  f"**Swiftness: **{current_pet.pet_stats[Stats.swt.value]}\n"
                                  f"**Vitality: **{current_pet.pet_stats[Stats.vit.value]}\n"
                                  f"**Smarts: **{current_pet.pet_stats[Stats.smt.value]}\n"
                                  f"**Instincts: **{current_pet.pet_stats[Stats.ins.value]}\n")
    return pet_data_msg


async def reroll_pet(ctx: Context, pet_name: str) -> Pet:
    rolls = PET_REROLLS
    current_pet = Pet(int(ctx.author.id), pet_name)
    while rolls > 0:
        pet_data_msg = await print_pet_info(ctx, current_pet)
        reroll_msg = await ctx.send(f"{ctx.author.mention} would your like to reroll? (Send \"**yes**\" or \"**no**\")\n"
                       f"**Remaining Rerolls: {rolls}**")

        replied = False
        while not replied:
            try:
                reply = await bot.wait_for('message', timeout=300.0)
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} You ran out of time to reroll.")
                return current_pet
            else:
                if reply.author.id == ctx.author.id:
                    if reply.content.lower() == 'yes' or reply.content.lower() == 'y':
                        current_pet = Pet(int(ctx.author.id), pet_name)
                        replied = True
                        await pet_data_msg.delete()
                        await reroll_msg.delete()
                    elif reply.content.lower() == 'no' or reply.content.lower() == 'n':
                        await ctx.send(f"{ctx.author.mention} Take care of them!")
                        return current_pet
                    else:
                        await ctx.send(f"{ctx.author.mention} Sorry I didn't understand that response. "
                                       f"(Send \"**yes**\" or \"**no**\")")
                    if reply.channel.id == PET_GENERAL:
                        await reply.delete()
        rolls -= 1

    await print_pet_info(ctx, current_pet)
    await ctx.send(f"{ctx.author.mention} Take care of them!")
    return current_pet


@bot.command()
async def pet(ctx: Context):
    if not ctx.channel.id == PET_GENERAL:
        await ctx.send(f"{ctx.author.mention} Please only use **!pet** in <#{PET_GENERAL}>")
        return

    author = ctx.author
    author_id = int(author.id)

    if not db_pets.check_pet(author_id):
        print(f"{ctx.author.name} does not have a pet yet.")
        await ctx.send(f"{author.mention} You do not have a pet yet.")

    current_pet = db_pets.get_pet(author_id)
    await print_pet_info(ctx, current_pet)


@bot.command()
async def newpet(ctx: Context):
    if not ctx.channel.id == PET_GENERAL:
        await ctx.send(f"{ctx.author.mention} Please only use **!newpet** in <#{PET_GENERAL}>")
        return

    author = ctx.author
    author_id = int(author.id)

    if db_pets.check_pet(author_id):
        print(f"{ctx.author.name} already has a pet.")
        await ctx.send(f"{author.mention} You already have a pet.")
        return

    command_msg = ctx.message.content.split()
    if not len(command_msg) == 2:
        print(f"{ctx.author.name} entered invalid newpet command.")
        await ctx.send(f"{author.mention} It should be **!newpet XXXXX** (**XXXXX** is your pets single word name.")
        return

    pet_name = command_msg[1].strip()
    current_pet = await reroll_pet(ctx, pet_name)
    db_pets.store_pet(author_id, current_pet)


@bot.command()
async def petemoji(ctx: Context):
    author = ctx.author
    author_id = author.id

    if author_id not in ADMIN_IDS:
        await ctx.send(f"{author.mention}, you do not have permission to use this.")
        return

    command_msg = ctx.message.content.split()
    if not len(command_msg) == 3:
        return

    await ctx.message.delete()

    target_id = int(command_msg[1].strip())

    if not db_pets.check_pet(target_id):
        print(f"They do not have a pet yet.")
        return

    desired_emoji = emoji.emojize(command_msg[2].strip())

    current_pet = db_pets.get_pet(target_id)
    current_pet.pet_emoji = desired_emoji
    db_pets.store_pet(target_id, current_pet)

    await ctx.send(f"{current_pet.name}'s emoji has been set to {desired_emoji}")


@bot.command()
async def resetpet(ctx: Context):
    author = ctx.author
    author_id = author.id
    if author_id not in ADMIN_IDS:
        await ctx.send(f"{author.mention}, you do not have permission to use this.")
        return

    command_msg = ctx.message.content.split()
    if not len(command_msg) == 2:
        return

    await ctx.message.delete()

    target_id = int(command_msg[1].strip())
    num_removed = db_pets.delete_pet(target_id)
    print(f"{num_removed} pet has been reset for {int(target_id)}.")
