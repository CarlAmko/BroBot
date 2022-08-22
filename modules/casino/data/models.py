import dataclasses
import random
from enum import Enum
from typing import List, Optional

from emoji import emojize

JACKPOT_BASE = 1000


class SlotMachineSizes(Enum):
    sml = 1
    med = 25
    lrg = 100

    @property
    def generate_key(self) -> str:
        return "777" + str(self.value)


class Suit(Enum):
	SPADES = 0
	HEARTS = 1
	CLUBS = 2
	DIAMONDS = 3


class Face(Enum):
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	SIX = 6
	SEVEN = 7
	EIGHT = 8
	NINE = 9
	TEN = 10
	JACK = 11
	QUEEN = 12
	KING = 13
	ACE = 14


@dataclasses.dataclass()
class Card:
	suit: Suit
	face: Face
	visible: bool = True

	def generate_msg(self) -> str:
		if self.visible:
			# Use number names for 1-10
			emoji_name = self.face.name.lower()
			# parse first letter for J-A
			if self.face.value > 10:
				emoji_name = f'regional_indicator_{emoji_name[0]}'
			elif self.face.value == 10:
				emoji_name = f'keycap_ten'

			value_emoji = emojize(f':{emoji_name}:')
			suit_emoji = emojize(f":{self.suit.name.lower()}:")
			return f'{value_emoji}{suit_emoji}'
		else:
			return emojize('<:card_back:1004886746376437880>')


class Hand:
	def __init__(self, cards: List[Card] = None):
		self.cards = cards if cards else []

	def add_to_hand(self, card: Card):
		self.cards.append(card)

	def top_card(self) -> Optional[Card]:
		return self.cards.pop() if self.cards else None


def generate_shuffled_deck() -> List[Card]:
	deck = [Card(suit, face) for suit in Suit for face in Face]
	random.shuffle(deck)
	return deck
