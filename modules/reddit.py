import time

import asyncpraw

import env
from modules import bot

reddit = asyncpraw.Reddit(
	client_id=env.REDDIT_CLIENT_ID,
	client_secret=env.REDDIT_CLIENT_SECRET,
	user_agent="BroBot"
)


@bot.command()
async def news(ctx):
	subreddit = await reddit.subreddit('gamernews')
	items = []
	async for item in subreddit.hot(limit=10):
		items.append((item.title, item.created, item.url))

	def parse_timestamp(epoch: int) -> str:
		return time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(epoch))

	await ctx.send(
		f'\n'.join([f"**{title}** ({parse_timestamp(created)})\n<{url}>\n" for title, created, url in items]))
