import http.server
import socketserver

import env
from bot import bot


@bot.event
async def on_ready():
	print(f'Logged in as {bot.user.name} -- {bot.user.id}.')


@bot.event
async def on_message(message):
	if not message.author.bot:
		await bot.process_commands(message)


# Start up web server to maintain connection on hosting provider
socketserver.TCPServer(('', env.port), http.server.SimpleHTTPRequestHandler).serve_forever()

print(f"Using bot secret token: {env.bot_secret}")
bot.run(env.bot_secret)
