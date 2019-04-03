import os
from dotenv import load_dotenv
from bot import bot
import modules.dice


async def on_ready():
	print(f'Logged in as {bot.user.name} -- {bot.user.id}.')


# async def on_message(message):
# 	if not message.author.bot:
# 		process_commands(message)

@bot.command(pass_context=True)
async def mention(ctx):
	msg = ctx.message
	await bot.say(f"{ctx.message.author.mention} said {msg.content}.")


@bot.command(pass_context=True)
async def joined(ctx):
	"""Says when a member joined."""
	user = ctx.message.author
	await bot.say(f"{user.mention} joined Discord on {user.joined_at}.")


@bot.command()
async def test():
	await bot.say("Test output command!")


# Load env vars
load_dotenv()

bot_secret = os.getenv("BOT_TOKEN")
print(f"Using bot secret token: {bot_secret}")

bot.run(bot_secret)
