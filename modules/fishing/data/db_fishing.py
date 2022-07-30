from database.db import db
from modules.fishing.data import fishing_location_data, item_data
from modules.fishing.data.models import FishingEquipment, FishingLocation


def get_fishing_location(user_id: int) -> FishingLocation:
	key = f'{user_id}:fishing:location'
	location_id = int(db.get(key)) if db.exists(key) else 1
	return fishing_location_data[location_id]


def update_fishing_location(user_id: int, new_location: FishingLocation):
	key = f'{user_id}:fishing:location'
	db.set(key, new_location.id)


def get_fishing_rod(user_id: int) -> FishingEquipment:
	key = f'{user_id}:fishing:rod'
	rod_id = int(db.get(key)) if db.exists(key) else 24
	rod = item_data[rod_id]

	if isinstance(rod, FishingEquipment):
		return rod
	else:
		raise RuntimeError(f'Somehow got non-Fishing Equipment item_id of {rod_id}')


def update_fishing_rod(user_id: int, new_rod: FishingEquipment):
	key = f'{user_id}:fishing:rod'
	db.set(key, new_rod.id)
