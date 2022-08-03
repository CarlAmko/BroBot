import json
import os
from typing import Dict

from modules.fishing.data.models import Item, FishingLocation, FishingEquipment

ITEM_DATA_PATH = os.path.join(os.path.dirname(__file__), 'items.json')
FISHING_LOCATION_DATA_PATH = os.path.join(os.path.dirname(__file__), 'fishing_locations.json')

with open(ITEM_DATA_PATH, 'r') as file:
	item_data: Dict[int, Item] = {}
	for item in json.load(file):
		if 'fishing_power' not in item:
			item_data[item['id']] = Item(**item)
		else:
			item_data[item['id']] = FishingEquipment(**item)

with open(FISHING_LOCATION_DATA_PATH, 'r') as file:
	fishing_location_data: Dict[int, FishingLocation] = \
		{location['id']: FishingLocation(**location) for location in json.load(file)}
