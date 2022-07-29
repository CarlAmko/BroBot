import random
from typing import List


class Item:
	def __init__(self, id: int, name: str, emoji: str, value: int, weight: float):
		self.id = id
		self.name = name
		self.emoji = emoji
		self.value = value
		self.weight = weight


class ItemProbability:
	def __init__(self, item_id: int, probability: int):
		self.item_id = item_id
		self.probability = probability


class FishingLocation:
	def __init__(self, id: int, name: str, fishing_probabilities: List[dict]):
		self.id = id
		self.name = name
		self.fishing_probabilities = [ItemProbability(**weight) for weight in fishing_probabilities]

		self._total_probability = sum(probability.probability for probability in self.fishing_probabilities)

	def catch_fish(self) -> int:
		# returned list is size of 1, so fine to use [0]
		choice = random.choices(self.fishing_probabilities,
		                        weights=[prob.probability for prob in self.fishing_probabilities])[0]
		return choice.item_id

	def _roll(self) -> int:
		return random.randint(1, self._total_probability)
