from bot import bot


@bot.command()
async def delrole(ctx):
	msg = ctx.message.content
	query = msg.split(' ')[1]
	match = next(filter(lambda role: role.name == query, ctx.guild.roles))
	try:
		await match.delete()
		await ctx.send(f'Successfully deleted role \'{query}\'.')
	except Exception as e:
		await ctx.send(f'Failed to delete role: {e}')


@bot.command()
async def roles(ctx):
	all_roles = [role.name for role in ctx.guild.roles][1:]
	await ctx.send(f'The server roles are:\n {all_roles}')
