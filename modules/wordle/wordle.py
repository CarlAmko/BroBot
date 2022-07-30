import json
import os.path
import random
from typing import Dict, Optional, List, Iterable, Set

import emoji
import requests
from discord import Member
from discord.ext.commands import Context

from database.db import get_currency, update_currency
from modules import bot

MAX_GUESSES = 6

words: Dict[int, Optional[str]] = {}
guesses_used: Dict[int, int] = {}
prev_guesses: Dict[int, List[str]] = {}
letter_mappings: Dict[str, Set[str]] = {}

wrong_guess = emoji.emojize(':black_large_square:')
correct_guess = emoji.emojize(':green_square:')
missed_guess = emoji.emojize(':yellow_square:')

WORD_DATA_PATH = os.path.join(os.path.dirname(__file__), '../fishing/data/words.json')


def _lookup_word(word: str) -> Dict:
	url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
	return requests.get(url).json()


def _is_valid_word(word: str) -> bool:
	resp = _lookup_word(word)
	return not ('title' in resp and resp['title'] == "No Definitions Found")


def _create_emoji_string(word: Iterable[str]) -> str:
	return ''.join((f":regional_indicator_{c}:" for c in word))


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

			letter_mappings[missed_guess] = set()
			letter_mappings[correct_guess] = set()
			letter_mappings[wrong_guess] = set()
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
		elif not _is_valid_word(guess):
			await ctx.send(f"{author.mention} '{guess}' is not a word.")
		else:
			word_to_guess = words[key]

			# Create a mapping of char -> set of indices
			chars_remaining = {c: set() for c in word_to_guess}
			for i, c in enumerate(word_to_guess):
				chars_remaining[c].add(i)

			# Create a result list.
			result = [wrong_guess for _ in range(len(guess))]
			# First pass: Find all chars in guess that are exactly correct and update result.
			for i, ch in enumerate(guess):
				if ch == word_to_guess[i]:
					result[i] = correct_guess
					letter_mappings[correct_guess].add(ch)
					# Remove this index from remaining chars
					chars_remaining[ch].remove(i)
					if len(chars_remaining[ch]) == 0:
						del chars_remaining[ch]

			# Second pass: Find all chars in guess that were missed and still exist in the word to guess.
			for i, ch in enumerate(guess):
				if result[i] != correct_guess:
					if ch in chars_remaining:
						result[i] = missed_guess
						letter_mappings[missed_guess].add(ch)
					else:
						letter_mappings[wrong_guess].add(ch)

			guesses_used[key] += 1
			remaining_guesses = MAX_GUESSES - guesses_used[key]

			guess_str = f'\n{_create_emoji_string(guess)}\n{"".join(result)}'
			prev_guesses[key].append(guess_str)
			await ctx.send(
				f'{author.mention}{"".join(prev_guesses[key])}\n\n'
				# f'{correct_guess}: {_create_emoji_string(letter_mappings[correct_guess])}\n'
				# f'{missed_guess}: {_create_emoji_string(letter_mappings[missed_guess])}\n'
				f'{wrong_guess}: {_create_emoji_string(letter_mappings[wrong_guess])}\n'
				f'**{remaining_guesses} guesses remaining**'
			)

			if guess == word_to_guess:
				current_balance = get_currency(key)
				earned_score = (2 * (remaining_guesses + 1))
				update_currency(key, current_balance + earned_score)
				await ctx.send(f'{author.mention} guessed correctly! You earned {earned_score} diggities.')
				del words[key]
			elif remaining_guesses == 0:
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
