import random

from modules import bot
from discord.ext.commands import Context
import emoji
from database.db import db

QUOTES_CHANNEL_ID = 871496158474821654
TIME_TO_DELETE = 86400
loading_emj = emoji.emojize("<a:loading:734622445910360105>")


@bot.command()
async def quote(ctx: Context):
    current_message = await ctx.send(f"Give me a sec to find something good. {loading_emj}")
    key = 'quotes'
    if not db.exists(key):
        quotes = await bot.get_channel(QUOTES_CHANNEL_ID).history(limit=None).flatten()
        content = []
        for current_quote in quotes:
            content.append(current_quote.content)
        db.setex(key, TIME_TO_DELETE, '###'.join(content))
    else:
        content = str(db.get(key)).split('###')

    random_quote = random.choice(content)
    await current_message.edit(content=random_quote)
