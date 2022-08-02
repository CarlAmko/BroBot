import random
import re

from modules import bot

MAX_SHOWN_DICE = 10
MAX_SHOWN_VALUE = 20


@bot.command()
async def r(ctx):
	msg = ctx.message
	text = msg.content

	async def invalid():
		await ctx.send("Invalid usage. Use as '!r NdX'. (N = number of nice, X = size of die)")

	# Check if input matches expected dice pattern
	# matches = re.findall(r"([\s0-9])d(\d{1,2})", text) or None
	matches = re.findall(r"(\s*\d+)d(\d+)", text) or None

	if matches:
		dice_str = matches[0]
		print(dice_str)
	else:
		await invalid()
		return

	num_dice, sides = dice_str[0], int(dice_str[1])
	# Cast string to int.
	num_dice = int(num_dice) if num_dice.strip() else 1

	print(f"Rolling {num_dice} d{sides}...")
	# Assemble roll result.
	msg = f"{msg.author.mention}\n"

	# Print result depending on number of dice rolled
	if num_dice <= MAX_SHOWN_DICE:
		await ctx.send(msg + print_all_dice(num_dice, sides))
	elif sides <= MAX_SHOWN_VALUE:
		await ctx.send(msg + print_each_value(num_dice, sides))
	else:
		await ctx.send(msg + print_total_only(num_dice, sides))


def roll_die(sides):
	# Return a random value from 1-X
	return random.randint(1, sides)


def print_all_dice(num_dice, sides):
	msg = ""
	total = 0

	for _ in range(num_dice):
		val = roll_die(sides)
		total += val
		msg += f"d{sides}: **{val}**\n"

	msg += f"Total: **{total}**"
	return msg


def print_each_value(num_dice, sides):
	msg = ""
	total = 0
	values = [0] * sides

	for i in range(num_dice):
		val = roll_die(sides)
		values[val - 1] += 1
		total += val

	for i in range(sides):
		msg += f"**{i + 1}:** rolled "

		if values[i] == 1:
			msg += f"**1** time.\n"
		else:
			msg += f"**{values[i]}** times.\n"

	msg += f"Total: **{total}**"
	return msg


def print_total_only(num_dice, sides):
	msg = ""
	total = 0

	for i in range(num_dice):
		val = roll_die(sides)
		total += val

	msg += f"Rolled **{num_dice} d{sides}** for a total of **{total}**"
	return msg
