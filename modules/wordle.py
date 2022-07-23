import json
import os.path
import random

import emoji
from discord import Member
from discord.ext.commands import Context

from db import db
from modules import bot

MAX_GUESSES = 6

num_guesses_used = 0
word_to_guess = None
chars_remaining = {}
prev_guess_stack = []

wrong_guess = emoji.emojize(':black_large_square:')
correct_guess = emoji.emojize(':green_square:')
missed_guess = emoji.emojize(':yellow_square:')

WORD_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data/words.json')


# noinspection PyTypeChecker
@bot.command()
async def wordle(ctx: Context):
    global word_to_guess, num_guesses_used, prev_guess_stack

    if word_to_guess is not None:
        await ctx.send(f"{ctx.author.mention} Game is already started.")
    else:
        with open(WORD_DATA_PATH, 'r') as data_file:
            words = json.load(data_file)
            while word_to_guess is None:
                candidate = random.choice(words)
                if candidate['score'] >= 1000 and ' ' not in candidate['word']:
                    word_to_guess = candidate['word']
                    # word_to_guess = 'brobot'
            num_guesses_used = 0
            prev_guess_stack = []
            await ctx.send('Wordle game started! Type !gw to guess a word or !clearwordle to stop a game in progress.')


@bot.command()
async def gw(ctx: Context):
    global word_to_guess, num_guesses_used, chars_remaining

    if not word_to_guess:
        await ctx.send("World game has not started. Type !wordle to start one.")
    else:
        guess: str = ctx.message.content.split(" ", 1)[1].lower()
        # Validate guesses
        author: Member = ctx.author
        if len(guess) != 6:
            await ctx.send(f"{author.mention} Guesses must be 6 characters")
        elif not guess.isalpha():
            await ctx.send(f"{author.mention} Guesses must contain only alphabetic characters")
        else:
            result = []
            chars_remaining = {c: set() for c in word_to_guess}
            for i, c in enumerate(word_to_guess):
                chars_remaining[c].add(i)

            for i, ch in enumerate(guess):
                if ch == word_to_guess[i]:
                    result.append(correct_guess)
                    # Remove this index from remaining chars
                    if i in chars_remaining[ch]:
                        chars_remaining[ch].remove(i)
                elif ch in chars_remaining and len(chars_remaining[ch]) > 0:
                    result.append(missed_guess)
                else:
                    result.append(wrong_guess)
            num_guesses_used += 1

            emoji_guess = ''.join((f":regional_indicator_{c}:" for c in guess))
            guess_str = f'\n{emoji_guess}\n{"".join(result)}'
            prev_guess_stack.append(guess_str)
            await ctx.send(
                f'{author.mention}{"".join(prev_guess_stack)}\n**{MAX_GUESSES - num_guesses_used} guesses remaining**'
            )

            if guess == word_to_guess:
                key = author.id
                current_score = int(db.get(key)) or 0
                db.set(key, current_score + 1)
                await ctx.send(f'{author.mention} guessed correctly! You now have {current_score + 1} points.')
                word_to_guess = None
                print(f'{author.id} now has {current_score + 1 } wordle points.')
            elif num_guesses_used == MAX_GUESSES:
                await ctx.send(f"Better luck next time! The word was '{word_to_guess}'")
                word_to_guess = None


@bot.command()
async def clearwordle(ctx: Context):
    global word_to_guess
    if word_to_guess is not None:
        word_to_guess = None
        await ctx.send("Wordle game canceled.")
    else:
        await ctx.send("Wordle game is not in progress.")
