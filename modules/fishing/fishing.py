import asyncio
import random
from enum import Enum
from typing import Dict

import emoji
from discord.ext.commands import Context

from modules import bot
from modules.fishing.data import fishing_location_data, item_data

MAX_TABLE_ROLL = 100
MIN_BITE_TIME = 3.0
MAX_BITE_TIME = 60.0
FISHING_COST = 1
TIME_TO_HOOK = 10.0


class FishingState(Enum):
	WAITING_FOR_BITE = 1
	FISH_BITING = 2
	HOOKING = 3


sessions: Dict[int, FishingState] = {}


async def _bite_timer(ctx: Context, fisher: int):
	time_to_bite = random.uniform(MIN_BITE_TIME, MAX_BITE_TIME)
	await asyncio.sleep(time_to_bite)

	if fisher in sessions and sessions[fisher] == FishingState.WAITING_FOR_BITE:
		sessions[fisher] = FishingState.FISH_BITING
		await ctx.send(f"**BITE!** {ctx.author.mention} has a fish on their line! Send **!hook** to catch.")
		await _hook_timer(ctx, fisher)
	else:
		# error??
		pass


async def _hook_timer(ctx: Context, fisher: int):
	await asyncio.sleep(TIME_TO_HOOK)

	if fisher in sessions and sessions[fisher] == FishingState.FISH_BITING:
		await ctx.send(f"{ctx.author.mention} Oh no. Seems it got away. Send **!fish** to recast.")
		del sessions[fisher]
	else:
		# error??
		pass


async def _catch_fish(ctx):
	# TODO: Update this fishing location as appropriate
	fishing_location = fishing_location_data[1]

	caught_fish_id = fishing_location.catch_fish()
	caught_fish = item_data[caught_fish_id]
	await ctx.send(f"{emoji.emojize(caught_fish.emoji)}")

	money_text = 'diggity' if caught_fish.value == 1 else 'diggities'
	await ctx.send(f"{ctx.author.mention} caught a {caught_fish.name}... Sold for **{caught_fish.value} {money_text}**.")


@bot.command()
async def fish(ctx: Context):
	fisher = ctx.author.id
	if fisher not in sessions:
		sessions[fisher] = FishingState.WAITING_FOR_BITE
		await ctx.send(f"{ctx.author.mention} You cast your line...")
		await _bite_timer(ctx, fisher)
	else:
		await ctx.send(f"{ctx.author.mention} You are already fishing.")


@bot.command()
async def hook(ctx: Context):
	fisher = ctx.author.id

	if fisher not in sessions:
		await ctx.send(f"{ctx.author.mention} You are not fishing right now. Send **!fish** to start fishing.")
	else:
		state = sessions[fisher]
		if state == FishingState.WAITING_FOR_BITE:
			await ctx.send(f"{ctx.author.mention} There was nothing on the line. Send **!fish** to recast.")
		elif state == FishingState.FISH_BITING:
			await _catch_fish(ctx)
			del sessions[fisher]
