from bot import bot
import random


@bot.command()
async def r(ctx):
	msg = ctx.message
	dice = msg.content

	async def invalid():
		await bot.say("Invalid usage. Must use format dX. (X=4,6,8,10,12,20)")

	# Attempt to see if input is in the valid format.
	try:
		dice = dice[(dice.index('d') + 1):]
	except ValueError:
		await invalid()
		return

	res = roll_die(int(dice))
	if res:
		await ctx.send(f"{msg.author.mention}\nRolling d{dice}: **{res}**")
	else:
		await invalid()


@bot.command()
async def fuckhead(ctx):
	await ctx.send("Happy Birthday Spencer!")


@bot.command()
async def rr(ctx):
	msg = ctx.message
	parts = msg.split()
	print(parts)

	if not parts[1] or not parts[1].split('d'):
		await ctx.send("Incorrect usage. Must use format NdX. (N=0+, X=4,6,8,10,12,20)")
	else:
		for _ in range(parts[1].split('d')[0]):
			await ctx.send(f"{msg.author}\n")


def roll_die(sides):
	valid_dice = [4, 6, 8, 10, 12, 20]

	# Must be a valid dice choice.
	if sides not in valid_dice:
		return

	# Return a random value from 1-X
	return random.randint(1, sides)
