from modules.fishing.data import FishingEquipment


def format_durability(item) -> str:
	return f'{item.value} uses remaining' if item.value > 0 else ''


def format_quantity(item) -> str:
	return f' x{item.quantity}' if item.quantity > 1 else ''


def format_fishing_power(item) -> str:
	return f'+{item.fishing_power} FP' if isinstance(item, FishingEquipment) else ''


def format_description(item) -> str:
	return item.description if isinstance(item, FishingEquipment) else ''
