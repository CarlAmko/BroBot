import random

from modules import bot
from discord.ext.commands import Context
import emoji
from database.db import db

QUOTES_ID = 871496158474821654
TIME_TO_DELETE = 86400
loading_emj = emoji.emojize("<a:loading:734622445910360105>")


@bot.command()
async def quote(ctx: Context):
    current_message = await ctx.send(f"Give me a sec to find something good. {loading_emj}")
    ids_namespace = f'{QUOTES_ID}:quote:flag'

    if not db.exists(ids_namespace) == 1:
        quotes = await bot.get_channel(QUOTES_ID).history(limit=None).flatten()
        quote_ids = []
        for current_quote in quotes:
            quote_namespace = f'{current_quote.id}:quote'
            db.setex(quote_namespace, TIME_TO_DELETE, str(current_quote.content))
            quote_ids.append(current_quote.id)

        db.setex(ids_namespace, TIME_TO_DELETE, str(quote_ids))
    else:
        quote_ids = eval(db.get(ids_namespace))

    random_quote = random.choice(quote_ids)
    selected_quote = str(db.get(f'{random_quote}:quote'))[2:-1]
    await current_message.edit(content=selected_quote)
