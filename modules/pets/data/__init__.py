import json
import os
from typing import Dict

from modules.pets.data.models import Pet

ITEMS_ARMORS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'armors.json')
ITEMS_CONSUMABLES_DATA_PATH = os.path.join(os.path.dirname(__file__), 'consumables.json')
ITEMS_SHIELDS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'shields.json')
ITEMS_WEAPONS_DATA_PATH = os.path.join(os.path.dirname(__file__), 'weapons.json')
