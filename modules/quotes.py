import random

from modules import bot
from discord.ext.commands import Context
import emoji
from database.db import db

QUOTES_ID = 871496158474821654
TIME_TO_DELETE = 60
# TIME_TO_DELETE = 86400
loading_emj = emoji.emojize("<a:loading:734622445910360105>")


@bot.command()
async def quote(ctx: Context):
    current_message = await ctx.send(f"Give me a sec to find something good. {loading_emj}")
    namespace = f'{QUOTES_ID}:quote'

    if not db.exists(namespace) == 1:
        quotes = await bot.get_channel(QUOTES_ID).history(limit=None).flatten()
        db.setex(namespace, TIME_TO_DELETE)
    else:
        quotes = db.get(namespace)

    random_quote = random.choice(quotes)
    await current_message.edit(content=(random_quote.content + f"\n{random_quote.jump_url}"))
