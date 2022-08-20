import random

from modules import bot
from discord.ext.commands import Context
import emoji

QUOTES_ID = 871496158474821654
loading_emj = emoji.emojize("<a:loading:734622445910360105>")


@bot.command()
async def quote(ctx: Context):
    current_message = await ctx.send(f"Give me a sec to find something good. {loading_emj}")
    quotes = await bot.get_channel(QUOTES_ID).history(limit=None).flatten()
    random_quote = random.choice(quotes)
    await current_message.edit(content=(random_quote.content + f"\n{random_quote.jump_url}"))
