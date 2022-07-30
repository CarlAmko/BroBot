from database.db import db
from modules.fishing.data import FishingLocation, fishing_location_data


def get_fishing_location(user_id: int) -> FishingLocation:
	key = f'{user_id}:fishing:location'
	location_id = int(db.get(key)) if db.exists(key) else 1
	return fishing_location_data[location_id]


def update_fishing_location(user_id: int, new_location: FishingLocation):
	key = f'{user_id}:fishing:location'
	db.set(key, new_location.id)
