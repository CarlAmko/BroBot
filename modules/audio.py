import asyncio

import discord
import emoji
from yt_dlp import YoutubeDL
from discord import VoiceClient
from discord.ext.commands import Context

from modules import bot

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0',
}

ffmpeg_options = {
	'options': '-vn',
}

ytdl = YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.url = data.get('url')

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def _leave_voice_channels():
	for client in bot.voice_clients:
		await client.disconnect()


def _is_in_voice_channel() -> bool:
	voice_clients = bot.voice_clients
	return len(voice_clients) > 0


@bot.command()
async def play(ctx: Context, url: str):
	author = ctx.author

	voice = author.voice
	if not voice:
		await ctx.send(f'{author.mention} is not in a voice channel! Please join a voice channel first.')
		return

	voice_clients = bot.voice_clients
	voice_client: VoiceClient = voice_clients[0] if len(voice_clients) > 0 else None

	# If not connected to any voice channel, connect to user.
	if not voice_client:
		voice_client = await voice.channel.connect()

	# If connected to a different voice channel than the user, change to user's voice channel.
	if voice_client.channel.name != voice.channel.name:
		await voice_client.disconnect()
		voice_client = await voice.channel.connect()

	audio = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
	# Stop any currently playing audio.
	voice_client.stop()
	# Play requested audio.
	voice_client.play(audio, after=lambda e: print(f'Player error: {e}') if e else None)

	await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))
	await ctx.send(f'**Now playing:** {audio.title}')


@bot.command()
async def stop(ctx: Context):
	voice_clients = bot.voice_clients
	if len(voice_clients) == 0:
		await ctx.send('No audio playing.')
	else:
		voice_client: VoiceClient = voice_clients[0]
		voice_client.stop()
		await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))


@bot.command()
async def pause(ctx: Context):
	voice_clients = bot.voice_clients
	if len(voice_clients) == 0:
		await ctx.send('No audio playing.')
	else:
		voice_client: VoiceClient = voice_clients[0]
		voice_client.pause()
		await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))


@bot.command()
async def resume(ctx: Context):
	voice_clients = bot.voice_clients
	if len(voice_clients) == 0:
		await ctx.send('No audio playing.')
	else:
		voice_client: VoiceClient = voice_clients[0]
		voice_client.resume()
		await ctx.message.add_reaction(emoji.emojize(':thumbs_up:'))


@bot.command()
async def volume(ctx: Context, new_volume: int):
	if ctx.voice_client is None:
		return await ctx.send("Not connected to a voice channel.")

	if ctx.voice_client.source:
		ctx.voice_client.source.volume = new_volume / 100
		await ctx.send(f"Changed volume to {new_volume}%")
	else:
		await ctx.send("No audio playing. Please play something first before attempting to change volume.")


async def check_if_alone():
	while True:
		if _is_in_voice_channel():
			for voice_client in bot.voice_clients:
				# Only one member means it's alone.
				print(voice_client.channel.members)
				if len(voice_client.channel.members) == 1:
					await voice_client.disconnect()
		# Loop every minute.
		await asyncio.sleep(60)
