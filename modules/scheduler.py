import asyncio
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

import pytz
import recurrent
from discord import Member
from discord.ext.commands import Context
from pytz import BaseTzInfo, UnknownTimeZoneError

from database.db import db
from modules import bot


@dataclass(frozen=True)
class ScheduledTask:
	context: Context
	what: Optional[str]
	when: datetime


scheduled_tasks: List[ScheduledTask] = []
queue_lock = asyncio.Lock()


def _create_scheduled_task(context: Context, tz: BaseTzInfo) -> Optional[ScheduledTask]:
	msg = context.message
	# split off command from message
	text = msg.content.split(" ", 1)[1]

	when = recurrent.parse(text)
	if when is not None:
		when = tz.localize(when)
		what = re.findall(r'(.*) (?:tomorrow|today|next|at|in)', text) or None
		return ScheduledTask(context=context, what=what[0], when=when)
	else:
		return None


async def process_scheduled_tasks():
	while True:
		async with queue_lock:
			for task in scheduled_tasks:
				tz = _get_timezone(task.context.author)
				if datetime.now(tz) >= task.when:
					context = task.context
					await context.send(f'{context.author.mention} You asked me to remind you to {task.what}.')
					scheduled_tasks.remove(task)

		# Sleep for 5 seconds before checking again.
		await asyncio.sleep(5)


@bot.command()
async def remind(ctx: Context):
	msg = ctx.message
	author = msg.author

	tz_info = _get_timezone(author)
	if not tz_info:
		await ctx.send(f'{author.mention}, you haven\'t set your timezone. Use **!timezone <timezone> first.**')
		return

	# Parse text into a ScheduledTask.
	task = _create_scheduled_task(ctx, tz_info)
	if task is not None:
		async with queue_lock:
			scheduled_tasks.append(task)

		await ctx.send(
			f'{author.mention} Ok, I\'ve scheduled at reminder for you at {task.when.strftime("%m/%d/%Y at %I:%M %p")}.')
	else:
		await ctx.send(f'{author.mention} Could not create reminder. Try describing the time differently.')


def _get_timezone_key(user: Member) -> str:
	return f'{user.id}:timezone'


def _get_timezone(user: Member) -> Optional[BaseTzInfo]:
	key = _get_timezone_key(user)
	try:
		return pytz.timezone(db.get(name=key))
	except Exception:
		return None


@bot.command()
async def timezone(ctx: Context):
	msg = ctx.message
	text = msg.content

	zone_text = text.split(" ", 1)[1]
	if not zone_text.startswith('US/'):
		zone_text = f'US/{zone_text}'

	try:
		zone = pytz.timezone(zone_text)
		key = _get_timezone_key(ctx.author)
		db.set(name=key, value=str(zone))
		await ctx.send(f'{msg.author.mention} Successfully set timezone to {zone}.')
	except UnknownTimeZoneError:
		await ctx.send(f'{msg.author.mention} unknown timezone \'{zone_text}\'. Please try again.')
