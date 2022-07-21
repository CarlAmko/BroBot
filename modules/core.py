from discord import Guild
from discord.abc import GuildChannel

import env
from modules import bot


def get_guild() -> Guild:
	return bot.get_guild(int(env.GUILD_ID))


def get_channel_by_id(id: int) -> GuildChannel:
	return get_guild().get_channel(id)


def get_members_channel() -> GuildChannel:
	return get_channel_by_id(env.MEMBER_CHANNEL_ID)
