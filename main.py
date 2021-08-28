#!/usr/bin/env python3
from discord import Guild, VoiceChannel, Member

import env
from modules import bot, dice, game_price, reddit, randomizer, poll, audio
from modules.core import get_guild, get_members_channel


async def adjust_member_count():
	guild: Guild = get_guild()
	if guild is not None:
		channel: VoiceChannel = get_members_channel(guild)
		if channel is not None:
			await channel.edit(reason=None, name=f'Members: {guild.member_count}')


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


if __name__ == '__main__':
	bot.run(env.bot_secret)
