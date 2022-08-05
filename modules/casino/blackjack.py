import asyncio
import math
from collections import deque
from typing import Dict, Optional, List, Deque

import emoji
from discord import Member, Message
from discord.ext.commands import Context

from database.db import update_currency, get_currency
from modules import bot
from modules.casino.data.models import Hand, Card, generate_shuffled_deck, Value

game_msg: Optional[Message] = None

turn_order: Deque[Member] = deque()
players: Dict[Member, Hand] = {}
wagers: Dict[Member, int] = {}

deck: List[Card] = []
house_hand: Optional[Hand] = None


def deal_cards():
	global house_hand
	# Deal two face-up cards to each player
	for player in players:
		players[player].add_to_hand(deck.pop())
		players[player].add_to_hand(deck.pop())

	# Deal face-up card to house
	house_hand = Hand()
	house_hand.add_to_hand(deck.pop())
	# Deal face-down card to house
	face_down = deck.pop()
	face_down.visible = False
	house_hand.add_to_hand(face_down)


async def display_table(ctx: Context):
	global game_msg
	msg = []
	for user, hand in players.items():
		cards = []
		for card in hand.cards:
			cards.append(card.generate_msg())

		card_msg = ' '.join(cards)
		total = get_hand_total(hand)
		bust_msg = emoji.emojize(':x:') if total > 21 else ''
		msg.append(f'{user.mention}\n{card_msg} {bust_msg}')

	cards = ''.join([card.generate_msg() for card in house_hand.cards])
	msg.append(f'House\n{cards}')

	player = turn_order[-1].mention if turn_order else 'The House'
	msg = '\n\n'.join(msg)
	to_send = f'{msg}\nIt is {player}\'s turn.'
	if not game_msg:
		game_msg = await ctx.send(to_send)
	else:
		await game_msg.edit(content=to_send)


def get_hand_total(hand: Hand) -> int:
	total = 0
	ace_count = 0
	for card in hand.cards:
		if card.value.value <= 10:
			total += card.value.value
		elif card.value == Value.ACE:
			# Assume greedy value of 11; correct later.
			ace_count += 1
			total += 11
		else:
			# Face card
			total += 10

	while total > 21 and ace_count > 0:
		total -= 10
		ace_count -= 1

	return total


def setup_game():
	global deck
	deck = generate_shuffled_deck()


def teardown():
	global deck, turn_order, players, house_hand, game_msg
	deck = []
	turn_order = deque()
	players = {}
	house_hand = None
	game_msg = None


@bot.command()
async def bjhelp(ctx: Context):
	msg = f'''Welcome to the blackjack tables.
	- The round begins 15 seconds after the first player places a wager.
	- To place a wager, type **!blackjack N**, where N is the amount you wish to bet.
	
	- The rules are simple; get as close to **21** without going over.
	- At the start of the round, all participating players will be dealt two cards face-up.
	- The house will be dealt one card face-up and one card face-down.
	- **Aces** are worth either **1** or **11**, depending on the other cards in your hand.
	- If the total value of cards in your hand exceed **21**, you will **bust** and forfeit your wager.
	
	- Play progresses in the order that players entered the game.
	- Each player will decide if they wish to **!stand** or **!hit**.
	- Choosing to **!stand** will end your turn. If you **!hit**, you will be dealt a card face-up.
	- You may continue to **!hit** until you either **bust** or decide to **!stand**. 
	- After all players have either stood or busted, the dealer will then do the same.
	
	- If the value of the dealer's hand exceeds **21**, all non-busted players will win automatically.
	- If the value of the dealer's hand exceeds the value of your hand, you lose and forfeit your wager.
	- If the value of the dealer's hand is lower than the value of your hand, you win!
	
	That's it! Have fun and good luck! {emoji.emojize(":smile:")} 
	'''
	await ctx.send(f'{ctx.author.mention}\n{msg}')


@bot.command()
async def blackjack(ctx: Context):
	author = ctx.author

	async def invalid():
		await ctx.send(
			f'{author.mention} Invalid wager. Send as **!blackjack N**, where N is the amount you wish to bet.')

	# Add player to the game if they aren't already in.
	if not house_hand:
		if author not in players:
			# Accept wager
			if ' ' not in ctx.message.content:
				await invalid()
				return

			wager = ctx.message.content.split(' ')[1]
			try:
				wager = int(wager)
				if wager < 1:
					await invalid()
					return

				if wager <= get_currency(author.id):
					update_currency(author.id, -wager)
					wagers[author] = wager
				else:
					await ctx.send(f'{author.mention} You cannot afford a wager of {wager}.')
					return
			except Exception:
				await invalid()
				return

			players[author] = Hand()
			turn_order.appendleft(author)
			if deck:
				await ctx.send(f'{author.mention} Wager of {wager} accepted. Good luck!')
		else:
			await ctx.send(f'{author.mention} You are already playing this round.')
	else:
		await ctx.send(f'{author.mention} Game is already in progress.')
		return

	# If this is the first player to start a game, kick off start timer.
	if not deck:
		await ctx.send('Blackjack started! Game will begin in 15 seconds.')
		setup_game()
		await asyncio.sleep(15)
		deal_cards()
		await display_table(ctx)


@bot.command()
async def stand(ctx: Context):
	author: Member = ctx.author
	if deck:
		# Peek the next player here; don't pop in the event the author isn't the current player.
		current_player = turn_order[-1]
		if current_player.id == author.id:
			# Now we can pop, since we've confirmed this is the correct player.
			await next_player(ctx)

		await ctx.message.delete()
	else:
		await ctx.send(f'{author.mention} Game is not in progress')


@bot.command()
async def hit(ctx: Context):
	author: Member = ctx.author
	if deck:
		# Peek the next player here; don't pop in the event the author isn't the current player.
		current_player = turn_order[-1]
		if current_player.id == author.id:
			next_card = deck.pop()
			players[current_player].add_to_hand(next_card)
			await display_table(ctx)

			hand_total = get_hand_total(players[current_player])
			if hand_total > 21:
				await next_player(ctx)

		await ctx.message.delete()
	else:
		await ctx.send(f'{author.mention} Game is not in progress')


async def next_player(ctx: Context):
	turn_order.pop()
	await display_table(ctx)

	# Check if house's turn to play
	if not turn_order:
		await play_house(ctx)


async def play_house(ctx: Context):
	# First, reveal house's hand.
	for card in house_hand.cards:
		card.visible = True

	non_busted = {player: hand for player, hand in players.items() if get_hand_total(hand) < 21}
	if len(non_busted) != 0:
		# Per the rules of Blackjack, the dealer **must** hit if <= 16, and **must** stand if >= 17.
		house_total = get_hand_total(house_hand)
		while house_total < 17:
			house_hand.add_to_hand(deck.pop())
			house_total = get_hand_total(house_hand)
		await display_table(ctx)

		winners = []
		if house_total > 21:
			await ctx.send('**BUST**!')
			# Add all non-busted players to winners.
			winners.extend(non_busted)
		elif house_total == 21:
			# No winners.
			await ctx.send('House wins! Better luck next time.')
		else:
			# Add all players with winning hands.
			for player, hand in non_busted.items():
				if get_hand_total(hand) > house_total:
					winners.append(player)
		await award_winners(ctx, winners)

	teardown()


async def award_winners(ctx: Context, winners: List[Member]):
	if winners:
		for winner in winners:
			# TODO: More if BJ
			# multiplier = 2.0 if winner
			earnings = wagers[winner] * 2
			update_currency(winner.id, earnings)

		msg = ' '.join([winner.mention for winner in winners])
		await ctx.send(f'Winners: {msg}')
	else:
		await ctx.send('There are no winners.')


@bot.command()
async def grant(ctx: Context):
	author = ctx.author
	update_currency(author.id, 100)
	await ctx.send(f'{author.mention} Granted 100 diggities.')
