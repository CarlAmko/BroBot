import random
import re

from modules import bot

valid_dice = [4, 6, 8, 10, 12, 20]


@bot.command()
async def r(ctx):
	msg = ctx.message
	text = msg.content

	async def invalid():
		await ctx.send("Invalid usage. Use as '!r NdX'. (N=0+, X=4,6,8,10,12,20)")

	# Check if input matches expected dice pattern
	matches = re.findall(r"([\s0-9])d(\d{1,2})", text) or None
	if matches:
		dice_str = matches[0]
		print(dice_str)
	else:
		await invalid()
		return

	num_dice, sides = dice_str[0], int(dice_str[1])
	# Must be a valid dice choice.
	if sides not in valid_dice:
		await invalid()
		return

	# Cast string to int.
	num_dice = int(num_dice) if num_dice.strip() else 1

	print(f"Rolling {num_dice} d{sides}...")
	# Assemble roll result.
	total = 0
	msg = f"{msg.author.mention}\n"
	for _ in range(num_dice):
		val = roll_die(sides)
		total += val
		msg += f"d{sides}: **{val}**\n"
	msg += f"Total: **{total}**"

	await ctx.send(msg)


def roll_die(sides):
	# Return a random value from 1-X
	return random.randint(1, sides)
