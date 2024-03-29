import operator
import random
from functools import reduce
from typing import List

MAX_BASE_ROLL = 100


class Item:
	def __init__(self, id: int, name: str, emoji: str, value: int, base_weight: float, quantity: int = 1):
		self.id = id
		self.name = name
		self.emoji = emoji
		self.value = value
		self.base_weight = base_weight
		self.quantity = quantity

	@property
	def cost(self):
		return self.value * self.quantity


class FishingEquipment(Item):
	def __init__(self, id: int, name: str, emoji: str, value: int, base_weight: float, fishing_power: int,
	             description: str, base_durability: int, quantity: int = 1):
		super().__init__(id, name, emoji, value, base_weight, quantity)
		self.fishing_power = fishing_power
		self.description = description
		self.base_durability = base_durability
		# Current durability defaults to base_durability
		self.durability = base_durability


class ItemThreshold:
	def __init__(self, threshold: int, item_ids: List[int]):
		self.threshold = threshold
		self.item_ids = item_ids


class FishingLocation:
	def __init__(self, id: int, name: str, emoji: str, fishing_thresholds: List[dict]):
		self.id = id
		self.name = name
		self.emoji = emoji
		self.fishing_thresholds = [ItemThreshold(**threshold) for threshold in fishing_thresholds]

	@property
	def fish_ids(self) -> List[int]:
		return reduce(operator.concat, [x.item_ids for x in self.fishing_thresholds])

	def catch_fish(self, fishing_power: int) -> int:
		roll = random.randint(1, MAX_BASE_ROLL) + fishing_power

		# Find max threshold <= roll
		max_threshold = None
		for threshold in self.fishing_thresholds:
			if roll >= threshold.threshold:
				max_threshold = threshold
			else:
				break

		# Second roll for item in bucket
		return random.choice(max_threshold.item_ids)
