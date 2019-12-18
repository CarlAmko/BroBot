import discord
from discord import Color

from bot import bot


@bot.command()
async def color(ctx):
	msg = ctx.message
	user = msg.author

	# split off command from message
	splits = msg.content.split(" ", 1)

	if len(splits) < 2:
		await ctx.send(f"{user} Invalid input. Please specify RGB as !color [0,255] [0,255] [0,255].")

	r, g, b = (int(n) for n in splits[1].split(' '))
	color_from_rgb = Color.from_rgb(r, g, b)

	all_roles = ctx.guild.roles
	try:
		# if role does not exist, attempt to create it
		if user.name not in [role.name for role in all_roles]:
			highest_role = user.roles[-1]
			new_role = await ctx.guild.create_role(name=user.name, permissions=highest_role.permissions,
			                                       colour=color_from_rgb)
			new_roles = user.roles
			new_roles.append(new_role)
			await user.edit(roles=new_roles)
			print(f'{user.name}\'s roles are now {user.roles}')
		else:
			user_role = next(filter(lambda role: role.name == user.name, all_roles))
			await user_role.edit(colour=color_from_rgb)

	except discord.errors.Forbidden as e:
		print(e)
		await ctx.send(f'BroBot does not have permission to change roles! :(')
		return

	# output success
	await ctx.send(f'{msg.author.mention} Success!')
