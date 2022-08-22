import asyncio

from modules import bot
from discord import Message

DEFAULT_EXPIRE_TIME = 15


async def expiring_msg(msg_to_delete: Message, expire_in=DEFAULT_EXPIRE_TIME):
    await asyncio.sleep(expire_in)
    await msg_to_delete.delete()
