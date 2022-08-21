from discord.ext.commands import Context
from database.db import update_currency, get_currency
from modules import bot
from modules.pets.data.models import Pet, Stats
from modules.pets.data import db_pets
import emoji
from env import ADMIN_IDS

nothing_emj = emoji.emojize("<:nothing:1004150080779059381>")


async def print_pet_info(ctx: Context, current_pet: Pet):
    await ctx.send(f"{ctx.author.mention} {emoji.emojize(current_pet.pet_emoji)}\n"
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


@bot.command()
async def pet(ctx: Context):
    author = ctx.author
    author_id = author.id

    if not db_pets.check_pet(author_id):
        print(f"{ctx.author.name} does not have a pet yet.")
        await ctx.send(f"{author.mention} You do not have a pet yet.")

    current_pet = db_pets.get_pet(author_id)
    await print_pet_info(ctx, current_pet)


@bot.command()
async def newpet(ctx: Context):
    author = ctx.author
    author_id = author.id

    if db_pets.check_pet(author_id):
        print(f"{ctx.author.name} already has a pet.")
        await ctx.send(f"{author.mention} You already have a pet.")

    command_msg = ctx.message.content.split()

    if not len(command_msg) == 2:
        print(f"{ctx.author.name} entered invalid newpet command.")
        await ctx.send(f"{author.mention} Invalid newpet command. It should be !newpet XXXXX (XXXXX is your pets single"
                       f" word name.")

    pet_name = command_msg[1].strip()
    current_pet = Pet(pet_name)
    await print_pet_info(ctx, current_pet)
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

    target_id = command_msg[1].strip()
    desired_emoji = emoji.emojize(command_msg[2].strip())
    if not db_pets.check_pet(author_id):
        print(f"They do not have a pet yet.")
        return

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

    target_id = command_msg[1].strip()
    target_user = bot.get_user(target_id)
    db_pets.delete_pet(target_id)
    print("Pet has been reset.")
