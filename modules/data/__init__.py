import json
import os

FISH_DATA_PATH = os.path.join(os.path.dirname(__file__), 'items.json')

with open(FISH_DATA_PATH, 'r') as fish_file:
	fish_json = json.load(fish_file)
