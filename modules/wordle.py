import json
import os.path
import random
from typing import Dict, Optional, List

import emoji
from discord import Member
from discord.ext.commands import Context

from db import db
from modules import bot

MAX_GUESSES = 6

words: Dict[int, Optional[str]] = {}
guesses_used: Dict[int, int] = {}
prev_guesses: Dict[int, List[str]] = {}

wrong_guess = emoji.emojize(':black_large_square:')
correct_guess = emoji.emojize(':green_square:')
missed_guess = emoji.emojize(':yellow_square:')

WORD_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data/words.json')


# noinspection PyTypeChecker
@bot.command()
async def wordle(ctx: Context):
	global words, guesses_used, prev_guesses

	author = ctx.author
	if author.id in words:
		await ctx.send(f"{ctx.author.mention} Game is already started.")
	else:
		with open(WORD_DATA_PATH, 'r') as data_file:
			word_json = json.load(data_file)
			while author.id not in words:
				candidate = random.choice(word_json)
				if candidate['score'] >= 1000 and ' ' not in candidate['word']:
					words[author.id] = candidate['word']
			guesses_used[author.id] = 0
			prev_guesses[author.id] = []
			await ctx.send(
				f'{author.mention} Wordle game started! Type !gw to guess a word or !clearwordle to stop a game in progress.'
			)


@bot.command()
async def gw(ctx: Context):
	global words, guesses_used, prev_guesses
	author: Member = ctx.author
	key: int = author.id

	if key not in words:
		await ctx.send(f"{author.mention} You have not started a Wordle game. Type !wordle to start one.")
	else:
		guess: str = ctx.message.content.split(" ", 1)[1].lower()
		# Validate guesses
		if len(guess) != 6:
			await ctx.send(f"{author.mention} Guesses must be 6 characters")
		elif not guess.isalpha():
			await ctx.send(f"{author.mention} Guesses must contain only alphabetic characters")
		else:
			word_to_guess = words[key]
			# Create a result list, defaulting to wrong guesses.
			result = [wrong_guess for _ in range(len(guess))]
			# Create a mapping of char -> set of indices
			chars_remaining = {c: set() for c in word_to_guess}
			for i, c in enumerate(word_to_guess):
				chars_remaining[c].add(i)

			# First pass: Find all chars in guess that are exactly correct and update result.
			for i, ch in enumerate(guess):
				if ch == word_to_guess[i]:
					result[i] = correct_guess
					# Remove this index from remaining chars
					chars_remaining[ch].remove(i)
					if len(chars_remaining[ch]) == 0:
						del chars_remaining[ch]

			# Second pass: Find all chars in guess that were missed and still exist in the word to guess.
			for i, ch in enumerate(guess):
				if result[i] != correct_guess and ch in chars_remaining:
					result[i] = missed_guess

			guesses_used[key] += 1

			emoji_guess = ''.join((f":regional_indicator_{c}:" for c in guess))
			guess_str = f'\n{emoji_guess}\n{"".join(result)}'
			prev_guesses[key].append(guess_str)
			await ctx.send(
				f'{author.mention}{"".join(prev_guesses[key])}\n**{MAX_GUESSES - guesses_used[key]} guesses remaining**'
			)

			if guess == word_to_guess:
				current_score = int(db.get(key)) if db.exists(key) else 0
				new_score = current_score + 1
				db.set(key, new_score)
				await ctx.send(f'{author.mention} guessed correctly! You now have {new_score} points.')
				del words[key]
			elif guesses_used[key] == MAX_GUESSES:
				await ctx.send(f"Better luck next time! The word was '{word_to_guess}'")
				del words[key]


@bot.command()
async def clearwordle(ctx: Context):
	global words

	author = ctx.author
	if author.id in words:
		del words[author.id]
		await ctx.send(f"{author.mention} Wordle game canceled.")
	else:
		await ctx.send(f"{author.mention} You do not have a Wordle game in progress.")
