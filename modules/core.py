from discord import Guild, VoiceChannel

import env
from modules import bot


def get_guild() -> Guild:
	return bot.get_guild(int(env.guild_id))


def get_members_channel(guild: Guild) -> VoiceChannel:
	return guild.get_channel(int(env.member_channel_id))
