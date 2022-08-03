from typing import Dict

from database.db import db
from modules.fishing.data import fishing_location_data, item_data
from modules.fishing.data.models import FishingEquipment, FishingLocation

_DEFAULT_FISHING_LOCATION_ID = 1


def get_fishing_location(user_id: int) -> FishingLocation:
	key = f'{user_id}:fishing:location'
	location_id = int(db.get(key)) if db.exists(key) else _DEFAULT_FISHING_LOCATION_ID
	return fishing_location_data[location_id]


def update_fishing_location(user_id: int, new_location: FishingLocation):
	key = f'{user_id}:fishing:location'
	db.set(key, new_location.id)


def get_fishing_inventory(user_id: int) -> Dict[int, FishingEquipment]:
	equipment = {}
	namespace = f'{user_id}:fishing:inventory'
	for item_id in db.hkeys(namespace):
		uses_remaining = db.hget(namespace, key=item_id)
		item = item_data[int(item_id)]
		if isinstance(item, FishingEquipment):
			# TODO: This is very bad implemented this way. We need to not adjust the in-memory copy of the item, as this
			# TODO:  copy is shared between all users. Likely want to move mutable per-user properties to a new db table.
			item.durability = int(uses_remaining)
			equipment[item.id] = item
		else:
			raise RuntimeError(f'Somehow got non-FishingEquipment item_id of {int(item_id)}')

	return equipment


def add_to_fishing_inventory(user_id: int, equipment: FishingEquipment):
	namespace = f'{user_id}:fishing:inventory'
	key = equipment.id
	db.hincrby(name=namespace, key=key, amount=equipment.quantity * equipment.base_durability)


def decrement_from_fishing_inventory(user_id: int, equipment: FishingEquipment, adjustment: int = -1):
	namespace = f'{user_id}:fishing:inventory'
	key = equipment.id
	if db.hexists(namespace, key=key):
		uses_remaining = int(db.hget(namespace, key=key))
		# Just remove the key if there are `adjustment` left
		if uses_remaining == -adjustment:
			db.hdel(namespace, key)
		else:
			# Otherwise decrement by `adjustment`.
			db.hincrby(namespace, key=key, amount=adjustment)
