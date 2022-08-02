import asyncio
import random
from enum import Enum
from typing import Dict

import emoji
from discord.ext.commands import Context

from database.db import update_currency, get_currency
from modules import bot
from modules.fishing.data import item_data
from modules.fishing.data.db_fishing import get_fishing_location, get_fishing_inventory, add_to_fishing_inventory, \
	decrement_from_fishing_inventory
from modules.fishing.formating import format_fishing_power, format_quantity, format_description, format_durability, \
	format_cost
from modules.fishing.shop import get_items_on_sale

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


async def _catch_fish(ctx: Context):
	user_id = ctx.author.id
	fishing_location = get_fishing_location(user_id)
	fishing_inventory = get_fishing_inventory(user_id).values()
	total_fishing_power = sum(item.fishing_power for item in fishing_inventory)

	caught_fish_id = fishing_location.catch_fish(total_fishing_power)
	caught_fish = item_data[caught_fish_id]
	await ctx.send(f"{emoji.emojize(caught_fish.emoji)}")
	await ctx.send(
		f"{ctx.author.mention} caught a **{caught_fish.name}**... Sold for {format_cost(caught_fish)}.")

	# Add money, remove from charges inventory
	update_currency(ctx.author.id, caught_fish.cost)
	for item in fishing_inventory:
		decrement_from_fishing_inventory(user_id, item)


@bot.command()
async def fish(ctx: Context):
	fisher = ctx.author.id
	fishing_location = get_fishing_location(fisher)

	if fisher not in sessions:
		sessions[fisher] = FishingState.WAITING_FOR_BITE
		rod_emoji = emoji.emojize(':fishing_pole_and_fish:')
		fishing_location_emoji = emoji.emojize(fishing_location.emoji)
		await ctx.send(
			f"{rod_emoji} {ctx.author.mention} casts their line at {fishing_location_emoji} **{fishing_location.name}**...")
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


@bot.command()
async def ledger(ctx: Context):
	user_id = ctx.author.id
	fishing_location = get_fishing_location(user_id)

	fishing_location_msg = f'{emoji.emojize(fishing_location.emoji)} **{fishing_location.name}**:'
	msg = []
	for fish_id in fishing_location.fish_ids:
		item = item_data[fish_id]
		msg.append(f'{emoji.emojize(item.emoji)} {item.name}')
	msg = ', '.join(msg)

	await ctx.send(f'{ctx.author.mention}\n{fishing_location_msg} {msg}')


@bot.command()
async def fishingshop(ctx: Context):
	author = ctx.author
	sale_items = get_items_on_sale()

	sale_msg = ''.join([
		f'\n{i + 1}. {emoji.emojize(item.emoji)} **{item.name}** ({format_fishing_power(item)}){format_quantity(item)}:'
		f' {format_cost(item)}\n{format_description(item)}'
		for i, item in enumerate(sale_items)
	])
	moneybag = emoji.emojize(':moneybag:')
	await ctx.send(f"{author.mention}\n{moneybag}Today's sales{moneybag}\n{sale_msg}")


@bot.command()
async def buy(ctx: Context):
	author = ctx.author
	user_id = author.id

	async def invalid():
		await ctx.send(f'{author.mention} Invalid usage of !buy; Send !buy N, where N is the shop item number.')

	buy_index = ctx.message.content.split(' ')
	if len(buy_index) < 2:
		await invalid()
		return
	try:
		buy_index = int(buy_index[1])
		store_items = get_items_on_sale()
		# Check that the buy index requested is valid.
		if buy_index > len(store_items):
			raise Exception()

		requested_item = store_items[buy_index - 1]
		currency_avail = get_currency(user_id)
		# Check if user can afford item.
		if currency_avail < requested_item.cost:
			await ctx.send(f'{author.mention} You do not have enough diggities to purchase **{requested_item.name}**.')
			return
		# Charge the user for the item.
		update_currency(user_id, -requested_item.cost)
		add_to_fishing_inventory(user_id, requested_item)
		await ctx.send(
			f'{author.mention} Successfully purchased {emoji.emojize(requested_item.emoji)}**{requested_item.name}**! Have a nice day {emoji.emojize(":smile:")}'
		)
	except Exception:
		await invalid()


@bot.command()
async def inventory(ctx: Context):
	author = ctx.author
	user_id = ctx.author.id

	inventory = get_fishing_inventory(user_id)
	if inventory:
		msg = ''.join([
			f'\n{emoji.emojize(item.emoji)} **{item.name}** ({format_fishing_power(item)}) {format_durability(item)}\n{format_description(item)}'
			for item in inventory.values()
		])
		await ctx.send(f'{author.mention}{msg}')
	else:
		await ctx.send(f'{author.mention} Your fishing inventory is empty.')
