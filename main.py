#!/usr/bin/env python3
from discord import Guild, Member, Client

import env
from modules.core import get_guild, get_members_channel

from modules import bot, core, admin, lib
if not env.BETA:
	from modules import audio, dice, game_price, poll, randomizer, reddit, scheduler, diggity, quotes, tell_em
	from modules.fishing import fishing
	from modules.casino import blackjack, slot_machine
	from modules.wordle import wordle


async def adjust_member_count():
	guild: Guild = get_guild()
	if guild is not None:
		channel = get_members_channel()
		if channel is not None:
			await channel.edit(name=f'Members: {guild.member_count}')


@bot.event
async def on_ready():
	print(f'Logged in as {bot.user.name} -- {bot.user.id}.')

	# Adjust guild members channel number.
	await adjust_member_count()


@bot.event
async def on_member_join(member: Member):
	await adjust_member_count()


@bot.event
async def on_member_remove(member: Member):
	await adjust_member_count()


@bot.event
async def on_message(message):
	if not message.author.bot:
		await bot.process_commands(message)


client = Client()

if __name__ == '__main__':
	bot.loop.create_task(scheduler.process_scheduled_tasks())
	bot.loop.create_task(audio.check_if_alone())
	bot.run(env.BOT_SECRET)
