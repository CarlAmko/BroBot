import json
import os
from typing import Dict

from models import Item, FishingLocation

ITEM_DATA_PATH = os.path.join(os.path.dirname(__file__), 'items.json')
FISHING_LOCATION_DATA_PATH = os.path.join(os.path.dirname(__file__), 'fishing_locations.json')

with open(ITEM_DATA_PATH, 'r') as file:
	item_data: Dict[int, Item] = {item['id']: Item(**item) for item in json.load(file)}

with open(FISHING_LOCATION_DATA_PATH, 'r') as file:
	fishing_location_data: Dict[int, FishingLocation] = \
		{location['id']: FishingLocation(**location) for location in json.load(file)}
