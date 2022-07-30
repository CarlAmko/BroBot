from typing import List

from modules.fishing.data import Item, item_data


# TODO: Update this
def get_items_on_sale() -> List[Item]:
	return [item_data[25], item_data[26]]
